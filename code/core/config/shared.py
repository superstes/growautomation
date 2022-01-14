# defines global variables

from os import environ as os_environ


# config set by service
def init():
    global CONFIG
    global AGENT
    global SERVER

    CONFIG = []
    AGENT = None
    SERVER = None


# todo: integrate most used ones as controller settings with hardcoded fallback values

# general settings
if 'GA_GROUP' in os_environ:
    GA_GROUP = os_environ['GA_GROUP']

else:
    GA_GROUP = 'ga'

CRYPTO_RECOGNITION_TEXT = '#crypto-recognition'
PATH_HOME_VENV = '/venv/bin'  # home prepended
SOCKET_SHUFFLE = False  # if unset SERVER.security will be evaluated
NONE_RESULTS = ['', 'None', None, ' ']
CONFIG_FILE_PATH = '/core/config/file/core.conf'
CENSOR_SYMBOL = '●'
MINIMAL_PROCESS_TIMEOUT = 2

# service settings
SVC_LOOP_INTERVAL = 60
SVC_MAX_STOP_COUNT = 3
SVC_WAIT_TIME = 3
THREAD_JOIN_TIMEOUT = 5
THREAD_DEFAULT_SLEEP_TIME = 600

# log settings
LOG_MAX_TRACEBACK_LENGTH = 5000
LOG_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S:%f'
LOG_SEPARATOR = ' | '
LOG_CENSOR_OUTPUT = CENSOR_SYMBOL * 12
LOG_SECRET_SETTINGS = ['sql_secret']
LOG_FILE_PERMS = 664
LOG_DIR_PERMS = 775

# device settings
REVERSE_CONDITION_INTERVAL = 60
REVERSE_CONDITION_MAX_RETRIES = None
REVERSE_KEY_TIME = 'time'
REVERSE_KEY_CONDITION = 'condition'
DEVICE_SCRIPT_PATH = "device/%s"
LOCK_MAX_WAIT = 120
LOCK_CHECK_INTERVAL = 15

