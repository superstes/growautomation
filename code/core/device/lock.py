# function to get and remove lock from instance

from core.utils.debug import debugger
from core.utils.debug import Log
from core.config.shared import LOCK_MAX_WAIT, LOCK_CHECK_INTERVAL

from time import time
from time import sleep


def get(instance) -> bool:
    start_time = time()

    while time() < start_time + LOCK_MAX_WAIT:
        if not instance.locked:
            instance.locked = True
            return True
        else:
            sleep(LOCK_CHECK_INTERVAL)

    debugger("device-lock | get | instance '%s' gave up to get lock after '%s' sec" % (instance.name, LOCK_MAX_WAIT))
    Log().write("Gave up to get lock for device '%s' after '%s' sec" % (instance.name, LOCK_MAX_WAIT))

    return False


def remove(instance):
    instance.locked = False
