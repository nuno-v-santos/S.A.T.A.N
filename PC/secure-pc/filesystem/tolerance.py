import logging


logger = logging.getLogger('tolerance')


def log_encryption_start(path: str, iv: bytes):
    logger.debug('Encrypting {path} with iv {iv}'.format(
        path=path,
        iv=iv.hex()
    ))


def log_encryption_end(path: str):
    logger.debug('Finished encrypting {}'.format(path))


def log_decryption_start(path: str):
    logger.debug('Decrypting {}'.format(path))


def log_decryption_end(path: str):
    logger.debug('Finished decrypting {}')
