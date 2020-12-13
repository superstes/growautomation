from core.factory import config
from core.factory.forge.blueprint import blueprint_dict


class Go:
    def __init__(self, supply_dict: dict):
        self.supply_dict = supply_dict

        self.key_controller = config.KEY_OBJECT_CONTROLLER

    def get(self) -> dict:
        # {
        #     object_controller: [instance_list],
        # }

        output_dict = {}

        return output_dict
