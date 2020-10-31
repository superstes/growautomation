# update file settings after loading settings from db
# uses controller object for config comparison
# needs to return a dict with setting:value pairs

from core.config import shared as shared_var

ADDITIONAL_SETTING_LIST = ['name']


def get(current_config: dict) -> dict:
    loaded_config = {}

    for key in shared_var.SYSTEM.parent_instance.setting_list:
        try:
            if key in shared_var.SYSTEM.setting_dict:
                loaded_config[key] = shared_var.SYSTEM.setting_dict[key]
            else:
                loaded_config[key] = shared_var.SYSTEM.parent_instance.setting_dict[key]
        except KeyError:
            loaded_config[key] = current_config[key]

    for key in ADDITIONAL_SETTING_LIST:
        loaded_config[key] = getattr(shared_var.SYSTEM, key)

    return loaded_config
