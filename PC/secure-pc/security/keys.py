import logging

from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes

from typing import Union, IO, AnyStr

from .interfaces import AsymmetricKeyManagementInterface, SymmetricKeyManagementInterface, KeyPair, Key
from .encryption import AES256Encryption


class RSAKeyManager(AsymmetricKeyManagementInterface):
    def __init__(self):
        self.logger = logging.getLogger('RSAKeyManager')

    def create_key_pair(self, size: int) -> KeyPair:
        self.logger.debug('Generating key of size {}'.format(size))
        private_key = RSA.generate(size)
        public_key = private_key.publickey()
        return KeyPair(private_key=private_key, public_key=public_key)

    def load_key(self, file: Union[str, IO[AnyStr]], password: str = None) -> Key:
        self.logger.debug('Loading key')
        if isinstance(file, str):
            with open(file, 'rb') as f:
                pem = f.read()
        else:
            pem = file.read()
        key = RSA.import_key(pem, passphrase=password)
        return key

    def store_key(self, key: Key, file: Union[str, IO[AnyStr]], password: str = None) -> None:
        self.logger.debug('Saving key')
        assert isinstance(key, RSA.RsaKey), 'Wrong key type'
        if isinstance(file, str):
            with open(file, 'wb') as f:
                f.write(key.exportKey(passphrase=password))
        else:
            file.write(key.exportKey(passphrase=password))

    def load_key_pair(self, file: Union[str, IO[AnyStr]], password: str = None) -> KeyPair:
        private_key = self.load_key(file, password)
        public_key = private_key.publickey()
        return KeyPair(private_key=private_key, public_key=public_key)

    def store_key_pair(self, key_pair: KeyPair, file: Union[str, IO[AnyStr]], password: str = None) -> None:
        private_key = key_pair.private_key
        self.store_key(private_key, file, password)


class AES256KeyManager(SymmetricKeyManagementInterface):
    """
    This class is responsible for handling AES-256
    key generation, storage and retrieval
    """

    def create_key(self, seed: bytes = None) -> Key:
        if seed is None:
            return get_random_bytes(32)
        return PBKDF2(seed, b'')  # FIXME add salt?

    def load_key(self, file: Union[str, IO[AnyStr]], password: str = None) -> Key:
        if isinstance(file, str):
            with open(file, 'rb') as f:
                key = f.read()
        else:
            key = file.read()
        if password is not None:
            file_key = self.create_key(password.encode('utf-8'))
            cipher = AES256Encryption(file_key, AES256Encryption.MODE_EAX)
            key = cipher.decrypt(key)
        return key

    def store_key(self, key: Key, file: Union[str, IO[AnyStr]], password: str = None) -> None:
        if password is not None:
            file_key = self.create_key(password.encode('utf-8'))
            cipher = AES256Encryption(file_key, AES256Encryption.MODE_EAX)
            key = cipher.encrypt(key)
        if isinstance(file, str):
            with open(file, 'wb') as f:
                f.write(key)
        else:
            file.write(key)
