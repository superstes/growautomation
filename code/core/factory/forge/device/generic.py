from core.factory import config
from core.utils.debug import Log


class Go:
    def __init__(self, blueprint, supply_list: list):
        self.blueprint = blueprint
        self.supply_list = supply_list
        self.logger = Log()

        self.key_id = config.DB_ALL_KEY_ID
        self.key_name = config.DB_ALL_KEY_NAME
        self.key_desc = config.DB_ALL_KEY_DESCRIPTION
        self.key_setting = config.SUPPLY_KEY_SETTING_DICT

        self.downlink_attribute = config.CORE_DOWNLINK_ATTRIBUTE

    def get_model(self):
        output_list = []

        self.logger.write(f'Building device model objects', level=8)

        for data_dict in self.supply_list:
            instance = self.blueprint(
                setting_dict=data_dict[self.key_setting],
                member_list=data_dict[config.SUPPLY_KEY_MEMBER_DICT][config.SUPPLY_GENERIC_KEY_MEMBER],
                object_id=data_dict[self.key_id],
                name=data_dict[self.key_name],
                description=data_dict[self.key_desc],
            )

            output_list.append(instance)

        return output_list

    def get_device(self):
        output_list = []

        self.logger.write(f'Building device objects', level=8)

        for data_dict in self.supply_list:
            if self.downlink_attribute in data_dict:
                instance = self.blueprint(
                    setting_dict=data_dict[self.key_setting],
                    object_id=data_dict[self.key_id],
                    name=data_dict[self.key_name],
                    description=data_dict[self.key_desc],
                    downlink=data_dict[self.downlink_attribute],
                )

            else:
                instance = self.blueprint(
                    setting_dict=data_dict[self.key_setting],
                    object_id=data_dict[self.key_id],
                    name=data_dict[self.key_name],
                    description=data_dict[self.key_desc],
                )

            output_list.append(instance)

        return output_list
