import io
import os
import yaml
import logging

from typing import List

from pubsub import pub

from securepc import constants

from securepc.util import async_publish

from securepc.exceptions import NoPasswordError

from securepc.security.encryption import AES256Encryption, RSAEncryption
from securepc.security.keys import AES256KeyManager, RSAKeyManager

from securepc.messaging.communication import BluetoothCommunication, SecureCommunication
from securepc.messaging.exceptions import TimeoutException

from securepc.filesystem.encryption import encrypt_all, decrypt_all

_instance = None


class _Application(object):
    def __init__(self):
        self.files = []
        self.phone_name = ''
        self.phone_address = ''
        self.running = True

        self.local_cipher = None

        self.phone_public_key = None
        self.computer_key_pair = None
        self.encrypted_file_key = None
        self.decrypted_file_key = None

        self.communication = BluetoothCommunication()
        pub.subscribe(self.mainloop, 'app_start')

        global _instance
        _instance = self # FIXME improve this singleton

        os.makedirs(constants.CONFIG_DIRECTORY, exist_ok=True)

    @property
    def public_key(self):
        return self.computer_key_pair.public_key

    def has_paired(self):
        return all(os.path.isfile(path) for path in constants.CONFIG_FILES)

    def define_password(self, password: str) -> None:
        """
        Define a new password. WARNING: THIS ASSUMES THERE WAS
        NO PASSWORD SET! TO CHANGE PASSWORD, USE change_password
        INSTEAD

        :param password: the new password
        """
        aes_key_manager = AES256KeyManager()
        local_key = aes_key_manager.create_key(password.encode('utf-8'))
        aes_cipher = AES256Encryption(local_key, mode=AES256Encryption.MODE_EAX)
        self.local_cipher = aes_cipher
        self.password = password

        encrypted_password_check = aes_cipher.encrypt(constants.PASSWORD_CHECK_STRING)
        with open(constants.PASSWORD_CHECK_PATH, 'wb') as f:
            f.write(encrypted_password_check)

    def validate_password(self, password: str) -> bool:
        """
        Checks if the given password matches the stored one.
        This password will be stored in the application.

        :param password: the password to validate
        :return: True if password is valid, False otherwise
        """
        aes_key_manager = AES256KeyManager()
        key = aes_key_manager.create_key(password.encode('utf-8'))
        aes_cipher = AES256Encryption(key, mode=AES256Encryption.MODE_EAX)
        with open(constants.PASSWORD_CHECK_PATH, 'rb') as f:
            ciphered_string = f.read()
        try:
            assert aes_cipher.decrypt(ciphered_string) == constants.PASSWORD_CHECK_STRING
        except: # File has been tampered with or password is incorrect
            return False

        self.local_cipher = aes_cipher
        self.password = password
        return True

    def load_files_list(self) -> List[str]:
        """
        Loads the encrypted files list from the configuration file.
        :param
        :return:
        """
        if self.local_cipher is None:
            raise NoPasswordError("No valid password has been inputted yet")
        if not os.path.isfile(constants.FILES_LIST_PATH):
            self.files = {}
            return []

        with open(constants.FILES_LIST_PATH, 'rb') as f:
            encrypted_files_list = f.read()
        decrypted_files_list = self.local_cipher.decrypt(encrypted_files_list)

        with io.StringIO(str(decrypted_files_list, 'utf-8')) as s:
            files_list = yaml.load(s)

        logger = logging.getLogger("model")
        logger.debug("Loaded files list is {}".format(files_list))

        self.files = files_list
        return files_list

    def save_files_list(self) -> None:
        """
        Encrypt and save the files list to the configuration file.
        """
        if self.local_cipher is None:
            raise NoPasswordError("No valid password has been inputted yet")

        with io.StringIO() as f:
            yaml.dump(self.files, f)
            files_list = f.getvalue()

        encrypted_files_list = self.local_cipher.encrypt(files_list.encode('utf-8'))
        with open(constants.FILES_LIST_PATH, 'wb') as f:
            f.write(encrypted_files_list)

    def accept_connection(self):
        """
        Accept a connection from the phone
        """
        self.communication.accept()
        self.phone_name, self.phone_address = self.communication.get_client_info()
        self.generate_asymmetric_keys()

    def generate_asymmetric_keys(self):
        """
        Generate and store a new RSA key pair
        :return: the generated public key
        """
        logging.debug("Generating asymmetric keys")
        rsa_key_manager = RSAKeyManager()
        self.computer_key_pair = rsa_key_manager.create_key_pair(2048)
        rsa_key_manager.store_key_pair(self.computer_key_pair, constants.PC_KEYS_PATH, self.password)
        return self.computer_key_pair.public_key

    def store_phone_key(self):
        RSAKeyManager().store_key(self.phone_public_key, constants.PHONE_KEYS_PATH, self.password)

    def load_phone_key(self):
        self.phone_public_key = RSAKeyManager().load_key(constants.PHONE_KEYS_PATH, self.password)

    def load_encrypted_file_key(self):
        self.encrypted_file_key = AES256KeyManager().load_key(constants.ENCRYPTED_FILE_KEY_PATH, self.password)

    def ensure_encryption(self) -> bool:
        """
        Makes sure no files are left encrypted from a crashed session.

        :return True if a crash was detected; False otherwise
        """
        if os.path.exists(constants.DECRYPTED_FILE_KEY_NAME):
            disk_key = AES256KeyManager().load_key(constants.DECRYPTED_FILE_KEY_PATH, self.password)
            encrypt_all(self.files, disk_key)
            os.remove(constants.DECRYPTED_FILE_KEY_PATH)
            return True
        return False

    def initial_exchange(self):
        session_key = self.communication.receive(self.computer_key_pair.public_key.size_in_bytes()) # Receive TEK
        rsa_private_cipher = RSAEncryption(self.computer_key_pair.private_key)
        session_key = rsa_private_cipher.decrypt(session_key)

        self.communication = SecureCommunication(self.communication, self.computer_key_pair.public_key)
        self.communication.symmetric_key = session_key

        phone_key = self.communication.receive(481) # Receive IV | phone_public[TEK]
        with io.BytesIO(phone_key) as f:
            self.phone_public_key = RSAKeyManager().load_key(f)

        self.store_phone_key()

        disk_key_mek = self.communication.receive(80) # receive IV | DEK(MEK)[TEK]
        AES256KeyManager().store_key(disk_key_mek, constants.ENCRYPTED_FILE_KEY_PATH, self.password)

        self.communication.close()

    def add_file(self, file: str):
        if os.path.exists(file) and not file in self.files:
            self.files.append(file)
            self.save_files_list()
            async_publish("file_list_changed", filelist=list(self.files))

    def remove_file(self, file: str):
        index = self.files.index(file)
        if index != -1:
            del self.files[index]
            async_publish("file_list_changed", filelist=list(self.files))

    def mainloop(self):
        self.load_phone_key()
        self.load_encrypted_file_key()

        self.communication = SecureCommunication(
            BluetoothCommunication(),
            self.phone_public_key,
            generate=True
        )

        while self.running:
            self.communication.accept()
            async_publish('connected')
            self.communication.send(self.encrypted_file_key)
            self.decrypted_file_key = self.communication.receive(64)
            self.decrypt_all()
            async_publish('decrypted')

            nonces = set()
            self.communication.set_timeout(constants.HEARTBEAT_TIMEOUT)
            while self.running:
                try:
                    nonce = int.from_bytes(self.communication.receive(), 'big')
                except TimeoutException:
                    async_publish('disconnected')
                    self.encrypt_all()
                    async_publish('encrypted')
                    break
                if nonce in nonces:
                    async_publish('bad_nonce')
                    self.exit()

    def encrypt_all(self):
        encrypt_all(self.files, self.decrypted_file_key)
        os.remove(constants.DECRYPTED_FILE_KEY_PATH)
        self.decrypted_file_key = None

    def decrypt_all(self):
        decrypt_all(self.files, self.decrypted_file_key)

    def exit(self):
        self.running = False


def get_instance():
    return _instance or _Application()
