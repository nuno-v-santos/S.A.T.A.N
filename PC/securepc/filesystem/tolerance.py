import os
import binascii
import threading
from securepc.filesystem.constants import LOG_PATH, LOG_DIR
from typing import Dict, NamedTuple


mutex = threading.Lock()

def synchronized(lock: threading.Lock):
    """
    Decorator for synchronizing a function
    with the given lock

    :param lock: the lock to use for synchronization
    :return: the decorated function
    """
    def wrap(f):
        def synchronized_function(*args, **kwargs):
            with lock:
                return f(*args, **kwargs)
        return synchronized_function
    return wrap


def ensure_log_exists(f):
    """
    Decorator to ensure the log directory exists before
    logging

    :return: the decorated function
    """
    def log_function(*args, **kwargs):
        if not os.path.isdir(LOG_DIR):
            os.makedirs(LOG_DIR, exist_ok=True)
        f(*args, **kwargs)
    return log_function



@synchronized(mutex)
@ensure_log_exists
def log_encryption_start(path: str):
    with open(LOG_PATH, 'a') as log_file:
        print("es:{path}".format(
            path=binascii.hexlify(path.encode('utf-8')),
        ), file=log_file)


@synchronized(mutex)
@ensure_log_exists
def log_encryption_end(path: str):
    with open(LOG_PATH, 'a') as log_file:
        print("ee:{path}".format(
            path=binascii.hexlify(path.encode('utf-8')),
        ), file=log_file)


@synchronized(mutex)
@ensure_log_exists
def log_decryption_start(path: str):
    with open(LOG_PATH, 'a') as log_file:
        print("ds:{path}".format(
            path=binascii.hexlify(path.encode('utf-8')),
        ), file=log_file)


@synchronized(mutex)
@ensure_log_exists
def log_decryption_end(path: str):
    with open(LOG_PATH, 'a') as log_file:
        print("de:{path}".format(
            path=binascii.hexlify(path.encode('utf-8')),
        ), file=log_file)

@synchronized(mutex)
def get_file_status() -> Dict[str, str]:
    """
    Get the current encryption status of all
    logged files
    :return: a dictionary mapping file paths to encryption status (encrypting, encrypted, decrypting, decrypted)
    """
    file_status = {}
    if not os.path.exists(LOG_PATH):
        return {}
    with open(LOG_PATH, 'r') as log_file:
        for line in log_file.readlines():
            fields = line.split(':')
            opcode = fields[0]
            try:
                path = str(bytes.fromhex(fields[1]), 'utf-8')
            except:
                continue # some error happened writing this line to the log, ignore it
            if opcode == 'ds':
                file_status[path] = 'decrypting'
            elif opcode == 'de':
                file_status[path] = 'decrypted'
            elif opcode == 'es':
                file_status[path] = 'encrypting'
            elif opcode == 'ee':
                file_status[path] = 'encrypted'
    return file_status

@synchronized(mutex)
def clear_log() -> None:
    """
    Delete the log file
    """
    if os.path.isfile(LOG_PATH):
        os.remove(LOG_PATH)
