import appdirs
import os

APP_NAME = 'secure-pc'

PASSWORD_CHECK_NAME = 'password_check'
FILES_LIST_NAME = 'files.yml'

PASSWORD_CHECK_PATH = os.path.join(appdirs.user_config_dir(APP_NAME), PASSWORD_CHECK_NAME)
FILES_LIST_PATH = os.path.join(appdirs.user_config_dir(APP_NAME), FILES_LIST_NAME)

PASSWORD_CHECK_STRING = b'All work and no play makes Jack a dull boy'
