import io
import os
import yaml
import logging
import constants

from typing import List

from securepc.security.encryption import AES256Encryption, RSAEncryption
from securepc.security.keys import AES256KeyManager, RSAKeyManager

from securepc.messaging.communication import BluetoothCommunication, SecureCommunication

from securepc.exceptions import NoPasswordError


_instance = None

class _Application(object):
    def __init__(self):
        self.files = []
        self.phone_name = ''
        self.phone_address = ''

        self.local_cipher = None

        self.phone_public_key = None
        self.computer_key_pair = None
        self.encrypted_file_key = None
        self.file_encryption_key = None

        self.communication = BluetoothCommunication()

        global _instance
        _instance = self # FIXME improve this singleton

        os.makedirs(constants.CONFIG_DIRECTORY, exist_ok=True)

    @property
    def public_key(self):
        return self.computer_key_pair.public_key

    def define_password(self, password: str) -> None:
        """
        Define a new password. WARNING: THIS ASSUMES THERE WAS
        NO PASSWORD SET! TO CHANGE PASSWORD, USE change_password
        INSTEAD

        :param password: the new password
        """
        self.password = password
        aes_key_manager = AES256KeyManager()
        local_key = aes_key_manager.create_key(password.encode('utf-8'))
        aes_cipher = AES256Encryption(local_key, mode=AES256Encryption.MODE_EAX)
        self.local_cipher = aes_cipher
        
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
        logging.debug("Begin pairing.")
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

    def initial_exchange(self):
        logging.debug("Receiving and decrypting session key")
        session_key = self.communication.receive(self.computer_key_pair.public_key.size_in_bytes()) # Receive TEK
        logging.debug("Decrypting session key")
        rsa_private_cipher = RSAEncryption(self.computer_key_pair.private_key)
        session_key = rsa_private_cipher.decrypt(session_key)

        self.communication = SecureCommunication(self.communication, self.computer_key_pair.public_key)
        self.communication.symmetric_key = session_key

        logging.debug("Receiving and decrypting phone's public key")
        phone_key = self.communication.receive(481) # Receive IV | phone_public[TEK]
        logging.debug("Phone key is {}".format(phone_key))
        with io.BytesIO(phone_key) as f:
            self.phone_public_key = RSAKeyManager().load_key(f)

        self.store_phone_key()


        logging.debug("Receiving and decrypting Disk Encryption Key (encrypted by Master Encryption Key)")
        disk_key_mek = self.communication.receive(80) # receive IV | DEK(MEK)[TEK]
        logging.debug("Disk Encryption Key (MEK) is {}".format(disk_key_mek.hex()))


        # FIXME we don't need this key
        logging.debug("Receiving and decrypting Disk Encryption Key (unencrypted)")
        disk_key = self.communication.receive(64)
        logging.debug("Disk Encryption Key (unencrypted) is {}".format(disk_key.hex()))

        logging.debug("Pairing complete.")


def get_instance():
    return _instance or _Application()
