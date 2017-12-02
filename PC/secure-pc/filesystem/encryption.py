import os
import shutil

from .constants import backup_dir
from .tolerance import *
from ..security.encryption import AES256Encryption, Key


def encrypt_file(path: str, key: Key) -> bytes:
    """
    Encrypts a file using AES-256 CTR mode
    :param path: the path to the file to encrypt
    :param key: the key to encrypt the file with
    :return: the nonce used in the encryption
    """
    with open(path, 'rb') as f:
        data = f.read()

    cipher = AES256Encryption(key, AES256Encryption.MODE_CTR)
    encrypted = cipher.encrypt(data)
    log_encryption_start(path, cipher.nonce)

    if not os.path.isdir(backup_dir):
        os.makedirs(backup_dir, 0o600, exist_ok=True)
    shutil.copy2(path, backup_dir)

    with open(path, 'wb') as f:
        f.write(encrypted)

    os.remove(os.path.join(backup_dir, os.path.basename(path)))
    log_encryption_end(path)

    return cipher.nonce


def decrypt_file(path: str, key: Key, nonce: bytes) -> None:
    """
    Decrypts a file using AES-256 CTR mode
    :param path: the path to the file to decrypt
    :param key: the key to decrypt the file with
    :return: the nonce that was used to encrypt the file with
    """
    with open(path, 'rb') as f:
        data = f.read()

    cipher = AES256Encryption(key, AES256Encryption.MODE_CTR)
    decrypted = cipher.decrypt(data, nonce=nonce)
    log_decryption_start(path)

    if not os.path.isdir(backup_dir):
        os.makedirs(backup_dir, 0o600, exist_ok=True)
    shutil.copy2(path, backup_dir)

    with open(path, 'wb') as f:
        f.write(decrypted)

    os.remove(os.path.join(backup_dir, os.path.basename(path)))
    log_decryption_end(path)
