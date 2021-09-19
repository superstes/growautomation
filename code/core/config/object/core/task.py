# core timer objects
#   generic timers like output-timer (how often should all output-conditions be checked) or backup-timer

from core.config.object.base import GaBase
from core.config.object.helper import set_attribute


class GaTaskDevice(GaBase):
    setting_list = ['timer', 'enabled', 'interval', 'target']

    def __init__(self, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # specific vars
        self.setting_dict = setting_dict
        # device instance vars
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaTaskDevice
        )

# i see currently no use for the grouping of system timers
# class GaTimerModel(GaBase):
#     def __init__(self, member_list: list, setting_dict: dict, **kwargs):
#         # inheritance from superclasses
#         super().__init__(**kwargs)
#         # specific vars
#         self.member_list = member_list
#         self.setting_dict = setting_dict


class SystemTask(GaBase):
    setting_list = ['timer']

    def __init__(self, setting_dict: dict, execute, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # specific vars
        self.setting_dict = setting_dict
        self.execute = execute
        # device instance vars
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=SystemTask
        )
