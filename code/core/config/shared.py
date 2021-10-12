# defines global variables

from os import environ as os_environ


# config set by service
def init():
    global CONFIG
    global SYSTEM

    CONFIG = []
    SYSTEM = None


# todo: integrate most used ones as controller settings with hardcoded fallback values

# general settings
GA_GROUP = 'ga'

if 'GA_GROUP' in os_environ:
    GA_GROUP = os_environ['GA_GROUP']

CRYPTO_RECOGNITION_TEXT = '#crypto-recognition'
SUBPROCESS_TIMEOUT = 60
PYTHON_VENV = '/home/ga_core/venv/bin'
SOCKET_SHUFFLE = None  # if unset SYSTEM.security will be evaluated
NONE_RESULTS = ['', 'None', None, ' ']
CONFIG_FILE_PATH = '/core/config/file/core.conf'
CENSOR_SYMBOL = '●'

# service settings
SVC_RUN_RELOAD_INTERVAL = 86400
SVC_RUN_STATUS_INTERVAL = 3600
SVC_RUN_LOOP_INTERVAL = 60
SVC_MAX_STOP_COUNT = 3
SVC_WAIT_TIME = 5
THREAD_FAIL_COUNT_SLEEP = 5
THREAD_FAIL_SLEEP = 600
THREAD_JOIN_TIMEOUT = 5
THREAD_DEFAULT_SLEEP_TIME = 600

# db settings
MARIADB_CONFIG_FILE = '/etc/mysql/mariadb.conf.d/50-server.cnf'
MARIADB_SOCKET_DEFAULT = '/run/mysqld/mysqld.sock'
MARIADB_SVC = 'mariadb.service'

# log settings
LOG_MAX_TRACEBACK_LENGTH = 5000
LOG_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S:%f'
LOG_SEPARATOR = ' | '
LOG_CENSOR_OUTPUT = CENSOR_SYMBOL * 12
LOG_SECRET_SETTINGS = ['sql_secret']
LOG_FILE_PERMS = 644

# device settings
REVERSE_CONDITION_INTERVAL = 60
REVERSE_CONDITION_MAX_RETRIES = None
REVERSE_KEY_TIME = 'time'
REVERSE_KEY_CONDITION = 'condition'
DEVICE_SCRIPT_PATH = "device/%s"
LOCK_MAX_WAIT = 120
LOCK_CHECK_INTERVAL = 15

