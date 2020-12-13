# condition objects (are used to setup complex conditions which must be met before an output device will be addressed)
#   holds its condition settings
#   must know
#     if it correlates with other conditions
#     the output device for which it is checked for

from core.config.object.base import *
from core.config.object.helper import *


class GaConditionMatch(GaBase):
    setting_list = ['special', 'value', 'operator', 'period', 'period_data', 'check']
    #   check -> how to process the data pulled from the period (max-/min-/avg-value)
    #   value -> data to compare to
    #   operator -> operator to use for data comparison
    #   period -> the time period from which to pull the data for the comparison

    def __init__(self, check_instance, setting_dict: dict, **kwargs):
        super().__init__(**kwargs)
        self.check_instance = check_instance
        self.setting_dict = setting_dict
        # dynamic instance vars
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaConditionMatch
        )
        # static vars
        self.data = None


class GaConditionLink(GaBase):
    setting_list = ['operator']

    def __init__(self, condition_match_dict: dict, condition_group_dict: dict, setting_dict: dict, **kwargs):
        super().__init__(description='Generic condition link', **kwargs)
        self.condition_match_dict = condition_match_dict  # need dict because of order
        self.condition_group_dict = condition_group_dict  # need dict because of order
        self.setting_dict = setting_dict
        # dynamic instance vars
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaConditionLink
        )
        # static vars
        self.processed = False


class GaConditionGroup(GaBase):
    setting_list = ['timer', 'enabled']

    def __init__(self, member_list: list, output_object_list: list, output_group_list: list, setting_dict: dict, **kwargs):
        super().__init__(**kwargs)
        self.member_list = member_list  # links that are grouped
        self.output_object_list = output_object_list  # actors that should be triggered if the condition is met
        self.output_group_list = output_group_list  # actors that should be triggered if the condition is met
        self.setting_dict = setting_dict
        # dynamic instance vars
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaConditionGroup
        )
        # static vars
        self.data = None
