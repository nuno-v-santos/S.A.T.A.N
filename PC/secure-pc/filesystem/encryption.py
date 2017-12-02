from ..security.encryption import AES256Encryption, Key
from .tolerance import *
from .constants import backup_dir

import os
import shutil


def encrypt_file(path: str, key: Key) -> None:
    with open(path, 'rb') as f:
        data = f.read()

    cipher = AES256Encryption(key, AES256Encryption.MODE_CTR)
    encrypted = cipher.encrypt(data)
    log_encryption_start(path, cipher.iv)

    if not os.path.isdir(backup_dir):
        os.mkdir(backup_dir, 0o600)
    shutil.copy2(path, backup_dir)

    with open(path, 'wb') as f:
        f.write(encrypted)

    os.remove(os.path.join(backup_dir, os.path.basename(path)))
    log_encryption_end(path)


def decrypt_file(path: str, key: Key, iv: bytes) -> None:
    with open(path, 'rb') as f:
        data = f.read()

    cipher = AES256Encryption(key, AES256Encryption.MODE_CTR)
    decrypted = cipher.decrypt(data, iv=iv)
    log_decryption_start(path)

    if not os.path.isdir(backup_dir):
        os.mkdir(backup_dir, 0o600)
    shutil.copy2(path, backup_dir)

    with open(path, 'wb') as f:
        f.write(decrypted)

    os.remove(os.path.join(backup_dir, os.path.basename(path)))
    log_decryption_end(path)
