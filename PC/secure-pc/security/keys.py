import logging

from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes

from .interfaces import AsymmetricKeyManagementInterface, SymmetricKeyManagementInterface, KeyPair, Key


class RSAKeyManager(AsymmetricKeyManagementInterface):
    def __init__(self):
        self.logger = logging.getLogger('RSAKeyManager')

    def create_key_pair(self, size: int) -> KeyPair:
        self.logger.debug('Generating key of size {}'.format(size))
        private_key = RSA.generate(size)
        public_key = private_key.publickey()
        return KeyPair(private_key=private_key, public_key=public_key)

    def load_key(self, path: str, password: str = None) -> Key:
        self.logger.debug('Loading key from {}'.format(path))
        with open(path, 'rb') as f:
            pem = f.read()
        key = RSA.import_key(pem, passphrase=password)
        return key

    def store_key(self, key: Key, path: str, password: str = None) -> Key:
        self.logger.debug('Saving key to {}'.format(path))
        assert isinstance(key, RSA.RsaKey), 'Wrong key type'
        with open(path, 'wb') as f:
            f.write(key.exportKey(password))

    def load_key_pair(self, path: str, password: str = None) -> KeyPair:
        private_key = self.load_key(path, password)
        public_key = private_key.publickey()
        return KeyPair(private_key=private_key, public_key=public_key)

    def store_key_pair(self, key_pair: KeyPair, path: str, password: str = None) -> None:
        private_key = key_pair.private_key
        self.store_key(private_key, path, password)


class AES256KeyManager(SymmetricKeyManagementInterface):
    """
    This class is responsible for handling AES-256
    key generation, storage and retrieval
    """

    def create_key(self, seed: bytes = None) -> Key:
        if seed is None:
            return get_random_bytes(32)
        return SHA256.new(seed)

    def load_key(self, path: str, password: str = None) -> Key:
        with open(path, 'rb') as f:
            key = f.read()
        if password is not None:
            file_key = self.create_key(password.encode('utf-8'))
            # TODO decrypt the key using file_key
        return key

    def store_key(self, key: Key, path: str, password: str = None) -> Key:
        if password is not None:
            file_key = self.create_key(password.encode('utf-8'))
            # TODO encrypt the key using file_key
        with open(path, 'wb') as f:
            f.write(key)
