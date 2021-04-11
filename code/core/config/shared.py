# defines global variables

from os import environ as os_environ


# config set by service
def init():
    global CONFIG
    global SYSTEM

    CONFIG = []
    SYSTEM = None


# hardcoded config
# todo: integrate as controller settings with hardcoded fallback values
CRYPTO_RECOGNITION_TEXT = '#crypto-recognition'
# STARTUP_DEBUG = True  # may not be needed any more -> since the startup_shared_vars were created
TASK_LOG = False
TEST = False
SUBPROCESS_TIMEOUT = 15
LOCK_MAX_WAIT = 120
LOCK_CHECK_INTERVAL = 15
GA_GROUP = 'ga'

if 'GA_GROUP' in os_environ:
    GA_GROUP = os_environ['GA_GROUP']

LOG_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S:%f'
LOG_SEPARATOR = ' | '
LOG_CENSOR_OUTPUT = '●●●●●●●●●'
LOG_SECRET_SETTINGS = ['sql_secret']
LOG_FILE_PERMS = 644

# todo: set as controller setting
PYTHON_VENV = '/home/ga_core/venv/bin'
