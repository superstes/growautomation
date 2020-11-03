# condition objects (are used to setup complex conditions which must be met before an output device will be addressed)
#   holds its condition settings
#   must know
#     if it correlates with other conditions
#     the output device for which it is checked for

from core.config.object.base import *


class GaCondition(GaBase):
    def __init__(self, check_instance, value, operator: str, period: int, **kwargs):
        super().__init__(**kwargs)
        self.check_instance = check_instance
        self.value_check = 'avg'
        self.special = None
        self.value = value  # data to compare to
        self.operator = operator  # operator to use for data comparison
        self.period_type = 'time'
        self.period = period  # the time period from which to pull the data for the comparison
        # todo: period in time(sec) or last x entries -> at best without another attribute -.-
        #  else i might want to implement a condition-setting table
        self.check = 'avg'  # how to process the data pulled from the period (max-/min-/avg-value)
        self.data = None


class GaConditionGroup(GaBase):
    def __init__(self, type_id: int, parent: int, member_list: list, setting_dict: dict, output_list: list, **kwargs):
        super().__init__(**kwargs)
        self.type_id = type_id
        self.member_list = member_list  # links and/or subgroups that are grouped
        self.setting_dict = setting_dict
        self.main = self.setting_dict['condition_main']
        # if self.main:
        #     self.output_list = output_list  # actors that should be triggered if the condition is met
        # else:
        #     self.output_list = []  # can only trigger actors if it is a main condition group
        # todo: implement in factory and supply, create test data
        #  maybe refactor member processing by supply
        #  or refactor the WHOLE FACTORY PROCESS since it has grows ugly xD
        self.data = None
        self.parent = parent


class GaConditionLink(GaBase):
    def __init__(self, member_list: list, operator: str, **kwargs):
        super().__init__(name='generic-link', description='Generic condition link', **kwargs)
        self.member_list = member_list  # condition objects that are linked; must be exactly 2
        self.operator = operator  # operator to use when the condition objects are processed
        self.processed = False
