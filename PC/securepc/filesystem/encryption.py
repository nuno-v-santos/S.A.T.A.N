import os
import shutil
import logging
from typing import List

from securepc.filesystem.tolerance import *
from securepc.filesystem.constants import BACKUP_DIR
from securepc.security.encryption import AES256Encryption, Key

_logger = logging.getLogger('file_encryption')

def encrypt_file(path: str, key: Key) -> None:
    """
    Encrypts a file using AES-256 EAX mode.
    The IV will be stored in the first 16 bytes of the file.

    :param path: the path to the file to encrypt
    :param key: the key to encrypt the file with
    """
    with open(path, 'rb') as f:
        data = f.read()

    cipher = AES256Encryption(key, AES256Encryption.MODE_EAX)
    encrypted = cipher.encrypt(data)
    log_encryption_start(path)

    if not os.path.isdir(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, 0o600, exist_ok=True)
    shutil.copy2(path, BACKUP_DIR)

    with open(path, 'wb') as f:
        f.write(encrypted)

    os.remove(os.path.join(BACKUP_DIR, os.path.basename(path)))
    log_encryption_end(path)


def decrypt_file(path: str, key: Key) -> None:
    """
    Decrypts a file using AES-256 EAX mode.
    The IV is assumed to be on the first 16 bytes of the file.

    :param path: the path to the file to decrypt
    :param key: the key to decrypt the file with
    """
    with open(path, 'rb') as f:
        data = f.read()

    cipher = AES256Encryption(key, AES256Encryption.MODE_EAX)
    decrypted = cipher.decrypt(data)
    log_decryption_start(path)

    if not os.path.isdir(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, 0o600, exist_ok=True)
    shutil.copy2(path, BACKUP_DIR)

    with open(path, 'wb') as f:
        f.write(decrypted)

    os.remove(os.path.join(BACKUP_DIR, os.path.basename(path)))
    log_decryption_end(path)


def encrypt_all(files: List[str], key: Key) -> None:
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
        if status in ('encrypting', 'decrypting') and os.path.isfile(backup):
            _logger.debug('Restoring {} from backup'.format(path))
            shutil.copy2(backup, path)
            if status == 'encrypting':
                status = 'decrypted' # in this case, the restored backup will be decrypted
        if status == 'decrypted':
            encrypt_file(path, key)

    for path in files:
        if path in file_status:
            continue  # We've already handled it
        encrypt_file(path, key)
    clear_log()


def decrypt_all(files: List[str], key: Key) -> None:
    """
    Decrypts all files given.

    :param files: list of paths to the files to decrypt
    :param key: the key to decrypt the files with
    """
    for path in files:
        decrypt_file(path, key)
