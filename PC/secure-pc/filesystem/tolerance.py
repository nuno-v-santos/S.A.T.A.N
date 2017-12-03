import logging
import threading
from .constants import LOG_PATH


logger = logging.getLogger('tolerance')
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
def log_encryption_start(path: str, nonce: bytes):
    logger.debug('Encrypting {path} with nonce {nonce}'.format(
        path=path,
        nonce=nonce.hex(),
    ))
    with open(LOG_PATH, 'a') as log_file:
        print("es:{path}:{nonce}".format(
            path=path.encode('utf-8').hex(),
            nonce=nonce.hex(),
        ), file=log_file)


@synchronized(mutex)
def log_encryption_end(path: str):
    logger.debug('Finished encrypting {}'.format(path))
    with open(LOG_PATH, 'a') as log_file:
        print("ee:{path}".format(
            path=path.encode('utf-8').hex(),
        ), file=log_file)


@synchronized(mutex)
def log_decryption_start(path: str):
    logger.debug('Decrypting {}'.format(path))
    with open(LOG_PATH, 'a') as log_file:
        print("ds:{path}".format(
            path=path.encode('utf-8').hex(),
        ), file=log_file)


@synchronized(mutex)
def log_decryption_end(path: str):
    logger.debug('Finished decrypting {}'.format(path))
    with open(LOG_PATH, 'a') as log_file:
        print("de:{path}".format(
            path=path.encode('utf-8').hex(),
        ), file=log_file)
