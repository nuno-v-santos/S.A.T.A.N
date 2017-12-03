import os
import logging
import threading
from .constants import LOG_PATH
from typing import Dict, NamedTuple


_logger = logging.getLogger('tolerance')
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


@synchronized(mutex)
def log_encryption_start(path: str):
    _logger.debug('Encrypting {path}'.format(
        path=path,
    ))
    with open(LOG_PATH, 'a') as log_file:
        print("es:{path}".format(
            path=path.encode('utf-8').hex(),
        ), file=log_file)


@synchronized(mutex)
def log_encryption_end(path: str):
    _logger.debug('Finished encrypting {}'.format(path))
    with open(LOG_PATH, 'a') as log_file:
        print("ee:{path}".format(
            path=path.encode('utf-8').hex(),
        ), file=log_file)


@synchronized(mutex)
def log_decryption_start(path: str):
    _logger.debug('Decrypting {}'.format(path))
    with open(LOG_PATH, 'a') as log_file:
        print("ds:{path}".format(
            path=path.encode('utf-8').hex(),
        ), file=log_file)


@synchronized(mutex)
def log_decryption_end(path: str):
    _logger.debug('Finished decrypting {}'.format(path))
    with open(LOG_PATH, 'a') as log_file:
        print("de:{path}".format(
            path=path.encode('utf-8').hex(),
        ), file=log_file)

@synchronized(mutex)
def get_file_status():
    logger.debug('Fetching all currently decrypted files from the log')
    _logger.debug('Fetching all currently decrypted files from the log')
    file_status: Dict[str, str] = {}
    with open(LOG_PATH, 'r') as log_file:
        for line in log_file.readlines():
            fields = line.split(':')
            opcode = fields[0]
            path = str(bytes.fromhex(fields[1]), 'utf-8')
            if opcode == 'ds':
                logging.debug("Found decryption-in-progress file at {}".format(path))
                file_status[path] = 'decrypting'
            elif opcode == 'de':
                logging.debug("File at {} was decrypted")
                file_status[path] = 'decrypted'
            elif opcode == 'es':
                logging.debug("Found encryption-in-progress file at {}".format(path))
                file_status[path] = 'encrypting'
            elif opcode == 'ee':
                logging.debug("File at {} was encrypted".format(path))
                file_status[path] = 'encrypted'
    return file_status
