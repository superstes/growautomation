# area objects (used to group/filter devices based on their physical location)
#   hold the information which devices are placed 'in them'
#   know if they themselves are nested inside another area

from ..base import *


class GaArea(GaBase):
    def __init__(self, area_member_list: list, area_parent, **kwargs):
        super().__init__(**kwargs)
        self.area_member_list = area_member_list
        self.area_parent = area_parent
