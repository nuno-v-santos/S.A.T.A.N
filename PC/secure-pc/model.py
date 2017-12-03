import io
import os
import yaml
import logging
import constants
from typing import List
from security.encryption import AES256Encryption
from security.keys import Key, KeyPair, AES256KeyManager
from exceptions import NoPasswordError

class Model(object):
    def __init__(self):
        self.files = []
        self.phone_name = ''
        self.phone_address = ''

        self.local_cipher = None

        self.phone_public_key = None
        self.computer_key_pair = None
        self.file_encryption_key = None
        self.session_key = None

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
        This password will be stored in the model.

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
        Loads the encrypted files list from the given path.
        :param path:
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
