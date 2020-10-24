# condition objects (are used to setup complex conditions which must be met before an output device will be addressed)
#   holds its condition settings
#   must know
#     if it correlates with other conditions
#     the output device for which it is checked for

from core.config.object.base import *


class GaCondition(GaBase):
    # need to rethink the concept
    def __init__(self, group, parent, sequence: int, device, data, condition: str, operator: str, **kwargs):
        super().__init__(**kwargs)
        self.group = group
        self.parent = parent
        self.sequence = sequence
        self.device = device
        self.data = data
        self.condition = condition
        self.operator = operator
