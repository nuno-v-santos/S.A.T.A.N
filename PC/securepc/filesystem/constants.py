import appdirs
import os
from securepc.constants import APP_NAME

LOG_NAME = 'secure_log.txt'
BACKUP_DIR = appdirs.user_cache_dir(APP_NAME)
LOG_DIR = appdirs.user_log_dir(APP_NAME)
LOG_PATH = os.path.join(LOG_DIR, LOG_NAME)
