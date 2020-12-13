# area objects (used to group/filter devices based on their physical location)
#   hold the information which devices are placed 'in them'
#   know if they themselves are nested inside another area

from core.config.object.base import *


class GaAreaGroup(GaBase):
    def __init__(self, area_member_list: list, **kwargs):
        super().__init__(**kwargs)
        self.area_member_list = area_member_list
