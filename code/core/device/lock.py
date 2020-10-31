# function to get and remove lock from instance

from time import time
from time import sleep

LOCK_MAX_WAIT = 120
LOCK_CHECK_INTERVAL = 15


def get(instance) -> bool:
    start_time = time()

    while time() < start_time + LOCK_MAX_WAIT:
        if not instance.locked:
            instance.locked = True
            return True
        else:
            sleep(LOCK_CHECK_INTERVAL)

    return False


def remove(instance):
    instance.locked = False
