# defines global variables


# config set by service
def init():
    global CONFIG
    global SYSTEM

    CONFIG = []
    SYSTEM = None


# hardcoded config
# todo: integrate as controller settings with hardcoded fallback values
CRYPTO_RECOGNITION_TEXT = '#crypto-recognition'
STARTUP_DEBUG = True
TASK_LOG = False
TEST = False
SUBPROCESS_TIMEOUT = 15
LOCK_MAX_WAIT = 120
LOCK_CHECK_INTERVAL = 15
