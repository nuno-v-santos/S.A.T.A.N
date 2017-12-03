import constants
from typing import Dict
from security.encryption import AES256Encryption
from security.keys import Key, KeyPair, AES256KeyManager

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

