from abc import ABCMeta, abstractmethod
from typing import NamedTuple, Union
from Cryptodome.PublicKey.RSA import RsaKey


Key = Union(RsaKey, bytes)
KeyPair = NamedTuple('KeyPair', [('public_key', Key), ('private_key', Key)])


class EncryptionInterface(metaclass=ABCMeta):
    """
    Abstract interface for encrypting and decrypting data.
    """
    @abstractmethod
    def encrypt(self, message: bytes) -> bytes:
        """
        :param message: message to encrypt
        :return: encrypted message
        """
        raise NotImplementedError

    def decrypt(self, message: bytes) -> bytes:
        """
        :param message: message to decrypt
        :return: decrypted message
        """
        raise NotImplementedError


class KeyManagementInterface(metaclass=ABCMeta):
    """
    Abstract interface for managing storage
    and retrial of cryptographic keys.
    """
    @abstractmethod
    def load_key(self, path: str, password: str = None) -> Key:
        """
        Load a key from the filesystem
        :param path: path for the key file
        :param password: password protecting the file (optional)
        :return: the key
        """
        raise NotImplementedError

    @abstractmethod
    def store_key(self, key: Key, path: str, password: str = None) -> Key:
        """
        Write a key to a file
        :param key: key to write
        :param path: path to write the file to
        :param password: password to protect the file (optional)
        :return:
        """
        raise NotImplementedError


class AsymmetricKeyManagementInterface(KeyManagementInterface):
    """
    Abstract interface for generating, storing and retrieving
    asymmetric keys.
    """
    @abstractmethod
    def create_key_pair(self, size: int) -> KeyPair:
        """
        Create a public-private key pair
        :param size: size of the keys (in bits)
        :return: the key pair
        """
        raise NotImplementedError

    @abstractmethod
    def load_key_pair(self, path: str, password: str = None) -> KeyPair:
        """
        Load a key pair from the filesystem
        :param path: path for the key pair file
        :param password: password protecting the file (optional)
        :return: the key pair
        """
        raise NotImplementedError

    @abstractmethod
    def store_key_pair(self, key_pair: KeyPair, path: str, password: str = None) -> None:
        """
        Write a key pair to a file
        :param key_pair: key pair to write
        :param path: path to write the file to
        :param password: password to protect the file (optional)
        :return:
        """
        raise NotImplementedError


class SymmetricKeyManagementInterface(KeyManagementInterface):
    """
    Abstract interface for generating, storing and retrieving
    symmetric keys.
    """
    @abstractmethod
    def create_key(self, size: int) -> Key:
        """
        Create a symmetric encryption key
        :param size: the size of the key (in bits)
        :return: the generated key
        """
        raise NotImplementedError
