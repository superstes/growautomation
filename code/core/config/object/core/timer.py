# core timer objects
#   generic timers like output-timer (how often should all output-conditions be checked) or backup-timer

from core.config.object.base import *


class GaTimerDevice(GaBase):
    def __init__(self, parent_instance, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # specific vars
        self.parent_instance = parent_instance
        self.setting_dict = setting_dict
        self.timer = setting_dict['timer']
        if 'enabled' in setting_dict:
            self.enabled = setting_dict['enabled']
        else:
            self.enabled = True


class GaTimerModel(GaBase):
    def __init__(self, member_list: list, setting_dict: dict, parent: int, type_id: int, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # specific vars
        self.type_id = type_id
        self.parent = parent
        self.member_list = member_list
        self.setting_dict = setting_dict
