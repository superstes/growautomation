# function to get and remove lock from instance

from core.config.shared import LOCK_MAX_WAIT, LOCK_CHECK_INTERVAL
from core.utils.debug import device_log

from time import time, sleep


def get(instance) -> bool:
    start_time = time()

    while time() < start_time + LOCK_MAX_WAIT:
        if not instance.locked:
            instance.locked = True
            return True
        else:
            sleep(LOCK_CHECK_INTERVAL)

    device_log(f"Gave up to get lock for device \"{instance.name}\" after \"{LOCK_MAX_WAIT}\" sec", add=instance.name, level=6)

    return False


def remove(instance):
    instance.locked = False
