# creates timer list from group and device objects
# returns tuple of two lists
#   1. list of all timers
#   2. list of all custom timers (if a device overwrites its model inheritance)


from core.config.object.device.input import *
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
            if isinstance(obj, ALLOWED_OBJECT_TUPLE) and obj.enabled:
                if category == 'object':
                    if 'timer' in obj.setting_dict:
                        custom_list.append(obj)
                elif category == 'group':
                    timer_list.append(obj)

    timer_list.extend(custom_list)

    return timer_list, custom_list
