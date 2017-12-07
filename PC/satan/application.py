import io
import os
import shutil
import yaml
import threading

from typing import List

from pubsub import pub

from satan import constants
from satan.filesystem.tolerance import clear_log

from satan.util import async_publish

from satan.exceptions import NoPasswordError

from satan.security.encryption import AES256Encryption, RSAEncryption
from satan.security.keys import AES256KeyManager, RSAKeyManager

from satan.messaging.communication import BluetoothCommunication, SecureCommunication
from satan.messaging.exceptions import TimeoutException

from satan.filesystem.encryption import encrypt_all, decrypt_all

_instance = None


class _Application(object):
    def __init__(self):
        self.files = []
        self.phone_name = ''
        self.phone_address = ''
        self.running = True
        self._unpair = False

        self.local_cipher = None

        self.phone_public_key = None
        self.computer_key_pair = None
        self.encrypted_file_key = None
        self.decrypted_file_key = None

        self.communication = BluetoothCommunication()
        pub.subscribe(self.mainloop, 'app_start')

        self.clean_up_lock = threading.Lock()

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
            self.files = []
            return []

        with open(constants.FILES_LIST_PATH, 'rb') as f:
            encrypted_files_list = f.read()
        decrypted_files_list = self.local_cipher.decrypt(encrypted_files_list)

        with io.StringIO(str(decrypted_files_list, 'utf-8')) as s:
            files_list = yaml.load(s)

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
        if os.path.exists(constants.DECRYPTED_FILE_KEY_PATH):
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
        """
        Add a file from the application's protected file list

        :param file: path to file to add
        :return: True if file was added; False otherwise
        """
        file = os.path.realpath(file)
        if os.path.exists(file) and not file in self.files:
            self.files.append(file)
            self.save_files_list()
            async_publish("file_list_changed", file_list=list(self.files))
            return True
        return False

    def remove_file(self, file: str):
        """
        Remove a file from the application's protected file list

        :param file: path to file to remove
        :return: True if file was removed; False otherwise
        """
        file = os.path.realpath(file)
        try:
            index = self.files.index(file)
        except ValueError:
            return False
        del self.files[index]
        self.save_files_list()
        async_publish("file_list_changed", file_list=list(self.files))
        return True

    def mainloop(self):
        self.load_phone_key()
        self.load_encrypted_file_key()

        self.communication = SecureCommunication(
            BluetoothCommunication(),
            self.phone_public_key,
            generate=True
        )

        while self.running:
            try:
                self.communication.accept(5)
            except TimeoutException:
                continue
            async_publish('connected')
            try:
                self.communication.send(self.encrypted_file_key)
                self.decrypted_file_key = self.communication.receive(64)
            except:
                continue  # Phone disconnected during key exchange, ignore
            AES256KeyManager().store_key(self.decrypted_file_key, constants.DECRYPTED_FILE_KEY_PATH, self.password)
            self.decrypt_all()
            async_publish('decrypted')

            nonces = set()
            self.communication.set_timeout(constants.HEARTBEAT_TIMEOUT)
            while self.running:
                try:
                    nonce = int.from_bytes(self.communication.receive(), 'big')
                except TimeoutException:
                    if not self._unpair: # We don't really need to cleanup since we'll exit
                        self.clean_up()
                    break
                if nonce in nonces:
                    async_publish('bad_nonce')
                    self.exit()

    def clean_up(self):
        with self.clean_up_lock:
            async_publish('disconnected')
            self.encrypt_all()
            async_publish('encrypted')

    def encrypt_all(self):
        if self.decrypted_file_key is not None:
            encrypt_all(self.files, self.decrypted_file_key)
            os.remove(constants.DECRYPTED_FILE_KEY_PATH)
            self.decrypted_file_key = None

    def decrypt_all(self):
        decrypt_all(self.files, self.decrypted_file_key)

    def unpair(self):
        self._unpair = True

    def exit(self):
        self.running = False
        if self._unpair:
            if os.path.isdir(constants.CONFIG_DIRECTORY):
                shutil.rmtree(constants.CONFIG_DIRECTORY)
            clear_log()
        else:
            self.clean_up()


def get_instance():
    return _instance or _Application()
