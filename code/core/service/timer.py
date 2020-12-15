# creates timer list from group and device objects
# returns tuple of two lists
#   1. list of all timers
#   2. list of all custom timers (if a device overwrites its model inheritance)

from core.factory import config

from core.config.object.device.input import GaInputDevice
from core.config.object.device.input import GaInputModel
from core.config.object.setting.condition import GaConditionGroup
from core.config.object.core.timer import GaTimerDevice


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
            if isinstance(obj, ALLOWED_OBJECT_TUPLE) and obj.enabled == 1:

                if category == config.KEY_OBJECT_INPUT:
                    if obj.timer != obj.parent_instance.timer:
                        custom_list.append(obj)

                elif category in [config.KEY_GROUP_INPUT, config.KEY_GROUP_CONDITION]:
                    timer_list.append(obj)

    timer_list.extend(custom_list)

    return timer_list, custom_list
