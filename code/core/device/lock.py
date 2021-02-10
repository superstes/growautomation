# function to get and remove lock from instance

from core.config import shared as shared_vars
from core.utils.debug import MultiLog, Log, debugger
from core.config.shared import LOCK_MAX_WAIT, LOCK_CHECK_INTERVAL

from time import time, sleep


def get(instance) -> bool:
    if shared_vars.SYSTEM.device_log == 1:
        logger = MultiLog([Log(), Log(typ='device', addition=instance.name)])
    else:
        logger = Log()

    start_time = time()

    while time() < start_time + LOCK_MAX_WAIT:
        if not instance.locked:
            instance.locked = True
            return True
        else:
            sleep(LOCK_CHECK_INTERVAL)

    debugger("device-lock | get | instance \"%s\" gave up to get lock after \"%s\" sec" % (instance.name, LOCK_MAX_WAIT))
    logger.write("Gave up to get lock for device \"%s\" after \"%s\" sec" % (instance.name, LOCK_MAX_WAIT), level=2)

    return False


def remove(instance):
    instance.locked = False
