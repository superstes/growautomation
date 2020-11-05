# condition objects (are used to setup complex conditions which must be met before an output device will be addressed)
#   holds its condition settings
#   must know
#     if it correlates with other conditions
#     the output device for which it is checked for

from core.config.object.base import *
from core.config.object.helper import *

# todo: implement condition-settings table; change supply and factory process


class GaCondition(GaBase):
    def __init__(self, check_instance, setting_dict: dict, **kwargs):
        super().__init__(**kwargs)
        self.check_instance = check_instance
        self.setting_dict = setting_dict
        # dynamic instance vars
        #   check -> how to process the data pulled from the period (max-/min-/avg-value)
        #   value -> data to compare to
        #   operator -> operator to use for data comparison
        #   period -> the time period from which to pull the data for the comparison
        setting_list = ['special', 'value', 'operator', 'period', 'period_data', 'check']
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=setting_list,
            instance=self,
            obj=GaCondition
        )
        # static vars
        self.data = None


class GaConditionGroup(GaBase):
    def __init__(self, type_id: int, member_list: list, setting_dict: dict, output_list: list, **kwargs):
        super().__init__(**kwargs)
        self.type_id = type_id
        self.member_list = member_list  # links and/or subgroups that are grouped
        self.output_list = output_list  # actors that should be triggered if the condition is met
        self.setting_dict = setting_dict
        # dynamic instance vars
        setting_list = ['timer', 'enabled']
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=setting_list,
            instance=self,
            obj=GaCondition
        )
        # static vars
        self.data = None


class GaConditionLink(GaBase):
    def __init__(self, member_dict: list, setting_dict: dict, **kwargs):
        super().__init__(name='generic-link', description='Generic condition link', **kwargs)
        self.member_dict = member_dict
        # condition objects that are linked; must be exactly 2;
        self.setting_dict = setting_dict
        # dynamic instance vars
        setting_list = ['operator']
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=setting_list,
            instance=self,
            obj=GaCondition
        )
        # static vars
        self.processed = False
