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
        self.value = value
        self.operator = operator
        self.period = period


class GaConditionGroup(GaBase):
    def __init__(self, type_id: int, parent: int, member_list: list, **kwargs):
        super().__init__(**kwargs)
        self.type_id = type_id
        self.member_list = member_list
        self.parent = parent


class GaConditionLink(GaBase):
    def __init__(self, member_list: list, operator: str, **kwargs):
        super().__init__(name='generic-link', description='Generic condition link', **kwargs)
        self.member_list = member_list
        self.operator = operator
