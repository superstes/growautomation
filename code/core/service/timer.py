# creates timer list from group and device objects
# returns tuple of two lists
#   1. list of all timers
#   2. list of all custom timers (if a device overwrites its model inheritance)

from core.config.object.device.input import GaInputDevice
from core.config.object.device.input import GaInputModel
from core.config.object.setting.condition import GaConditionGroup
from core.config.object.core.timer import GaTimerDevice
from core.utils.debug import Log

logger = Log()


ALLOWED_OBJECT_TUPLE = (
    GaInputDevice,
    GaInputModel,
    GaConditionGroup,
    GaTimerDevice
)


def get(config_dict: dict) -> tuple:
    timer_list = []
    custom_list = []

    for category, obj_list in config_dict.items():
        for obj in obj_list:
            if isinstance(obj, ALLOWED_OBJECT_TUPLE):
                if obj.enabled == 1:

                    if isinstance(obj, GaInputDevice):
                        if obj.timer is not None and obj.timer != obj.parent_instance.timer:
                            custom_list.append(obj)

                    elif isinstance(obj, (GaInputModel, GaConditionGroup)):
                        timer_list.append(obj)

                else:
                    logger.write("Instance \"%s\" is disabled" % obj, level=4)

            else:
                logger.write("Object \"%s\" is not allowed" % obj, level=6)

    timer_list.extend(custom_list)

    return timer_list, custom_list
