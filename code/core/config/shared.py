# defines global variables


# config set by service
def init():
    global CONFIG
    global SYSTEM

    CONFIG = []
    SYSTEM = None


# hardcoded config
CRYPTO_RECOGNITION_TEXT = '#crypto-recognition'
STARTUP_DEBUG = True
TASK_LOG = False
TEST = False
