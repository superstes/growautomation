# handle device multi-logging

from core.config import shared as shared_vars
from core.utils.debug import MultiLog, Log


def device_logger(addition: str):
    from inspect import stack as inspect_stack
    from inspect import getfile as inspect_getfile
    if shared_vars.SYSTEM.device_log == 1:
        return MultiLog([
            Log(src_file=inspect_getfile(inspect_stack()[1][0])),
            Log(typ='device', addition=addition, src_file=inspect_getfile(inspect_stack()[1][0]))
        ])
    else:
        return Log(src_file=inspect_getfile(inspect_stack()[1][0]))
