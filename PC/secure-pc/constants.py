import appdirs
import os

APP_NAME = 'secure-pc'
PASSWORD_CHECK_NAME = 'password_check'
PASSWORD_CHECK_PATH = os.path.join(appdirs.user_config_dir(APP_NAME), PASSWORD_CHECK_NAME)
PASSWORD_CHECK_STRING = b'All work and no play makes Jack a dull boy'