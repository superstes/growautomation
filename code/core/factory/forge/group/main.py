# creates generic grouping instances

from core.factory import config
from core.factory.forge.blueprint import blueprint_dict
from core.factory.forge.group.area import Go as AreaGroup


class Go:
    def __init__(self, factory_dict: dict, supply_dict: dict):
        self.factory_dict = factory_dict
        self.supply_dict = supply_dict

        self.key_area_group = config.KEY_GROUP_AREA

    def get(self) -> dict:
        # {
        #     area_group: [instance_list],
        # }

        output_dict = {
            self.key_area_group: AreaGroup(
                supply_list=self.supply_dict[self.key_area_group],
                factory_dict=self.factory_dict,
                blueprint=blueprint_dict[self.key_area_group],
            ).get()
        }

        return output_dict

