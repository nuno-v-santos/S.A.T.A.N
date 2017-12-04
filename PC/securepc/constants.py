import appdirs
import os

APP_NAME = 'securepc'


PASSWORD_CHECK_NAME = 'password_check'
FILES_LIST_NAME = 'files.yml'
PC_KEYS_NAME = 'rsa_key_pc.bin'
PHONE_KEYS_NAME = 'rsa_key_phone.bin'

CONFIG_DIRECTORY = appdirs.user_config_dir(APP_NAME)

PASSWORD_CHECK_PATH = os.path.join(appdirs.user_config_dir(APP_NAME), PASSWORD_CHECK_NAME)
FILES_LIST_PATH = os.path.join(appdirs.user_config_dir(APP_NAME), FILES_LIST_NAME)
PC_KEYS_PATH = os.path.join(appdirs.user_config_dir(APP_NAME), PC_KEYS_NAME)
PHONE_KEYS_PATH = os.path.join(appdirs.user_config_dir(APP_NAME), PHONE_KEYS_NAME)

CONFIG_FILES = [
    PASSWORD_CHECK_PATH,
    FILES_LIST_PATH,
    PC_KEYS_PATH,
    PHONE_KEYS_PATH
]

PASSWORD_CHECK_STRING = b'All work and no play makes Jack a dull boy'
