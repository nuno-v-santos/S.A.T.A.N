import os
import shutil
import logging

from .constants import BACKUP_DIR
from .tolerance import *
from ..security.encryption import AES256Encryption, Key

_logger = logging.getLogger('file_encryption')

def encrypt_file(path: str, key: Key, nonce: bytes = None) -> bytes:
    """
    Encrypts a file using AES-256 CTR mode
    :param path: the path to the file to encrypt
    :param key: the key to encrypt the file with
    :param nonce: the nonce (iv) to encrypt the file with (if None, one will be generated)
    :return: the nonce used in the encryption
    """
    with open(path, 'rb') as f:
        data = f.read()

    cipher = AES256Encryption(key, AES256Encryption.MODE_EAX)
    encrypted = cipher.encrypt(data, nonce=nonce)
    log_encryption_start(path, cipher.nonce, cipher)

    if not os.path.isdir(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, 0o600, exist_ok=True)
    shutil.copy2(path, BACKUP_DIR)

    with open(path, 'wb') as f:
        f.write(encrypted)

    os.remove(os.path.join(BACKUP_DIR, os.path.basename(path)))
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

    cipher = AES256Encryption(key, AES256Encryption.MODE_EAX)
    decrypted = cipher.decrypt(data, nonce=nonce)
    log_decryption_start(path)

    if not os.path.isdir(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, 0o600, exist_ok=True)
    shutil.copy2(path, BACKUP_DIR)

    with open(path, 'wb') as f:
        f.write(decrypted)

    os.remove(os.path.join(BACKUP_DIR, os.path.basename(path)))
    log_decryption_end(path)


def encrypt_all(files: Dict[str, bytes], key: Key) -> None:
    """
    Encrypts all files that need to be encrypted, even those
    that may have remained decrypted and are logged.
    Log is cleared once this function returns successfully.

    :param files: a dictionary mapping file paths to their encryption IVs
    :param key: the key to encrypt the files with
    """
    file_status = get_file_status()
    for path, status in file_status.items():
        backup = os.path.join(BACKUP_DIR, os.path.basename(path))
        if path not in files:  # Maybe some voodoo magic happened and we no longer care about this file
            if os.path.isfile(backup):
                os.remove(backup)  # We don't want to have a backup we don't need
            continue
        if status in ('encrypting', 'decrypting'):
            if os.path.isfile(backup):
                _logger.debug('Restoring {} from backup'.format(path))
                shutil.copy2(backup, path)
                status = 'decrypted'
        if status == 'decrypted':
            encrypt_file(path, key, files[path])

    for path, nonce in files.items():
        if path in file_status:
            continue  # We've already handled it
        encrypt_file(path, key, nonce)
    clear_log()


def decrypt_all(files: Dict[str, bytes], key: Key) -> None:
    """
    Decrypts all files.

    :param files: dictionary mapping file paths to their encryption IVs
    :param key: the key to decrypt the files with
    """
    for path, nonce in files.items():
        decrypt_file(path, key, nonce)
