# creates timer list from group and device objects
# returns tuple of two lists
#   1. list of all timers
#   2. list of all custom timers (if a device overwrites its model inheritance)

from core.config.object.device.input import GaInputDevice
from core.config.object.device.input import GaInputModel
from core.config.object.setting.condition import GaConditionGroup
from core.config.object.core.task import GaTaskDevice
from core.utils.debug import log
from core.service.system_tasks import get_tasks


ALLOWED_OBJECT_TUPLE = (
    GaInputDevice,
    GaInputModel,
    GaConditionGroup,
    GaTaskDevice
)


def get(config_dict: dict) -> list:
    timer_list = get_tasks()

    for category, obj_list in config_dict.items():
        for obj in obj_list:
            if isinstance(obj, ALLOWED_OBJECT_TUPLE):
                if obj.enabled == 1:

                    if isinstance(obj, GaInputDevice):
                        if obj.timer is not None and obj.timer != obj.parent_instance.timer:
                            timer_list.append(obj)

                    elif isinstance(obj, (GaInputModel, GaConditionGroup)):
                        timer_list.append(obj)

                else:
                    log(f"Is disabled: \"{obj}\"", level=6)

            else:
                log(f"Is not allowed: \"{obj}\"", level=7)

    return timer_list
