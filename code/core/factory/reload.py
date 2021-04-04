# is called if the service is reloaded
# will find out if some object config has changed
# if so - the service will reload all threads with the new config

# stateful reload todo's:
#   need to have a list of instances(old) of which the config has changed
#   stop all timers etc. off those instances
#     linked instances (group) must also be processed
#   re-create those instances via the factory
#   start the timers for those new instances
#   profit

from core.factory.main import get as factory

from json import dumps as json_dumps


class Go:
    def __init__(self, object_list: list, config_dict: dict):
        self.object_list = object_list
        self.config_dict = config_dict
        self.new_object_list, self.new_config_dict = factory()

    def get(self) -> tuple:
        return self._reload_check(), self.new_object_list, self.new_config_dict

    def _reload_check(self) -> bool:
        # True = must reload
        # False = is ok
        new_json = json_dumps(self.new_config_dict, sort_keys=True, default=str)
        old_json = json_dumps(self.config_dict, sort_keys=True, default=str)

        if new_json == old_json:
            return False

        return True
