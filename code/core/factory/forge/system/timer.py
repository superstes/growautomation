from core.factory import config


class Go:
    def __init__(self, blueprint, supply_list: list):
        self.blueprint = blueprint
        self.supply_list = supply_list

        self.key_id = config.DB_ALL_KEY_ID
        self.key_name = config.DB_ALL_KEY_NAME
        self.key_desc = config.DB_ALL_KEY_DESCRIPTION
        self.key_setting = config.SUPPLY_KEY_SETTING_DICT

    def get(self):
        output_list = []

        for data_dict in self.supply_list:
            instance = self.blueprint(
                setting_dict=data_dict[self.key_setting],
                object_id=data_dict[self.key_id],
                name=data_dict[self.key_name],
                description=data_dict[self.key_desc],
            )

            output_list.append(instance)

        return output_list
