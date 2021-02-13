# handle device multi-logging

from core.config import shared as shared_vars
from core.utils.debug import MultiLog, Log


def device_logger(addition: str):
    if shared_vars.SYSTEM.device_log == 1:
        return MultiLog([Log(), Log(typ='device', addition=addition)])
    else:
        return Log()
