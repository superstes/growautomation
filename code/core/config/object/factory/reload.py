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

from core.config.object.factory.factory import Go as Factory


class Go:
    def __init__(self, object_list: list, config_dict: dict):
        self.object_list = object_list
        self.config_dict = config_dict
        self.new_object_list, self.new_config_dict = Factory().get()

    def get(self) -> tuple:
        return self._compare(), self.new_object_list, self.new_config_dict

    def _compare(self) -> bool:
        change_dict = {}

        for key, value in self.config_dict.items():
            if value != self.new_config_dict[key]:
                change_dict[key] = self.new_config_dict[key]

        if len(change_dict) > 0:
            return False
        else:
            return True
