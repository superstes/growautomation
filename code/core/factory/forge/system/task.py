from core.factory import config
from core.utils.debug import log


class Go:
    def __init__(self, blueprint, supply_data: dict):
        self.blueprint = blueprint
        self.supply_data = supply_data

    def get(self):
        output_list = []
        log(f'Building task objects', level=8)

        for data_dict in self.supply_data.values():
            instance = self.blueprint(
                setting_dict=data_dict[config.SUPPLY_KEY_SETTING_DICT],
                object_id=data_dict[config.DB_ALL_KEY_ID],
                name=data_dict[config.DB_ALL_KEY_NAME],
                description=data_dict[config.DB_ALL_KEY_DESCRIPTION],
            )

            output_list.append(instance)

        return output_list
