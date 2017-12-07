import appdirs
import os

APP_NAME = 'satan' # Smartphone As a Token Also Nonces
APP_VERBOSE_NAME = 'S.A.T.A.N.: Smartphone As a Token. Also, Nonces!'


PASSWORD_CHECK_NAME = 'password_check'
FILES_LIST_NAME = 'files.yml'
PC_KEYS_NAME = 'rsa_key_pc.bin'
PHONE_KEYS_NAME = 'rsa_key_phone.bin'
ENCRYPTED_FILE_KEY_NAME = 'enc_file_key.bin'
DECRYPTED_FILE_KEY_NAME = 'dec_file_key.bin'


CONFIG_DIRECTORY = appdirs.user_config_dir(APP_NAME)

PASSWORD_CHECK_PATH = os.path.join(CONFIG_DIRECTORY, PASSWORD_CHECK_NAME)
FILES_LIST_PATH = os.path.join(CONFIG_DIRECTORY, FILES_LIST_NAME)
PC_KEYS_PATH = os.path.join(CONFIG_DIRECTORY, PC_KEYS_NAME)
PHONE_KEYS_PATH = os.path.join(CONFIG_DIRECTORY, PHONE_KEYS_NAME)
ENCRYPTED_FILE_KEY_PATH = os.path.join(CONFIG_DIRECTORY, ENCRYPTED_FILE_KEY_NAME)
DECRYPTED_FILE_KEY_PATH = os.path.join(CONFIG_DIRECTORY, DECRYPTED_FILE_KEY_NAME)

CONFIG_FILES = [
    PASSWORD_CHECK_PATH,
    PC_KEYS_PATH,
    PHONE_KEYS_PATH,
    ENCRYPTED_FILE_KEY_PATH,
]

PASSWORD_CHECK_STRING = b'All work and no play makes Jack a dull boy'

HEARTBEAT_TIMEOUT = 35
