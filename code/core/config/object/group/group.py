# group objects (used to group/filter devices generically)
#   hold the information of their members
#   know if they themselves are nested inside another group

from core.config.object.base import *


class GaObjectGroup(GaBase):
    def __init__(self, group_member_list: list, **kwargs):
        super().__init__(**kwargs)
        self.group_member_list = group_member_list
