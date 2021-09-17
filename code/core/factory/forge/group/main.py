# creates generic grouping instances

from core.factory import config
from core.factory.forge.blueprint import blueprint_dict
from core.factory.forge.group.area import Go as AreaGroup
from core.utils.debug import log


class Go:
    def __init__(self, factory_data: dict, supply_data: dict):
        self.factory_data = factory_data
        self.supply_data = supply_data

        self.key_area_group = config.KEY_GROUP_AREA

    def get(self) -> dict:
        # {
        #     area_group: [instance_list],
        # }

        log(f'Building group objects (all)', level=8)

        output_dict = {
            self.key_area_group: AreaGroup(
                supply_list=self.supply_data[self.key_area_group],
                factory_dict=self.factory_data,
                blueprint=blueprint_dict[self.key_area_group],
            ).get()
        }

        return output_dict

