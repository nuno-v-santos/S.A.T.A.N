import logging


logger = logging.getLogger('tolerance')


def log_encryption_start(path: str, nonce: bytes):
    logger.debug('Encrypting {path} with nonce {nonce}'.format(
        path=path,
        nonce=nonce.hex()
    ))


def log_encryption_end(path: str):
    logger.debug('Finished encrypting {}'.format(path))


def log_decryption_start(path: str):
    logger.debug('Decrypting {}'.format(path))


def log_decryption_end(path: str):
    logger.debug('Finished decrypting {}')
