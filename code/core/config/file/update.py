# update file settings after loading settings from db
# uses controller object for config comparison
# needs to return a dict with setting:value pairs

from core.config import shared as config

ADDITIONAL_SETTING_LIST = ['name']


def get(current_config: dict) -> dict:
    loaded_config = {}

    for key in config.AGENT.setting_list:
        try:
            loaded_config[key] = config.AGENT.setting_dict[key]

        except KeyError:
            loaded_config[key] = current_config[key]

    for key in ADDITIONAL_SETTING_LIST:
        loaded_config[key] = getattr(config.AGENT, key)

    return loaded_config
