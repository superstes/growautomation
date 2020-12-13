# creates instances for single-conditions

from core.utils.debug import debugger
from core.factory import config


class Go:
    def __init__(self, blueprint, supply_list: list, input_object_dict: dict):
        self.blueprint = blueprint
        self.supply_list = supply_list
        self.input_object_dict = input_object_dict

        self.key_id = config.DB_ALL_KEY_ID
        self.key_name = config.DB_ALL_KEY_NAME
        self.key_desc = config.DB_ALL_KEY_DESCRIPTION
        self.key_setting = config.SUPPLY_KEY_SETTING_DICT

    def get(self) -> list:
        output_list = []

        for data_dict in self.supply_list:
            instance = self.blueprint(
                name=data_dict[self.key_name],
                description=data_dict[self.key_desc],
                setting_dict=data_dict[self.key_setting],
                check_instance=self._get_check_instance(data_dict=data_dict),
                object_id=data_dict[self.key_id],
            )

            output_list.append(instance)

        return output_list

    def _get_check_instance(self, data_dict: dict):
        for key, instance_list in self.input_object_dict.items():
            if key == config.KEY_GROUP_INPUT:
                check_key = config.DB_CONDITION_MATCH_KEY_INPUT_GROUP
            else:
                check_key = config.DB_CONDITION_MATCH_KEY_INPUT_OBJECT

            for instance in instance_list:
                if data_dict[check_key] is not None and instance.object_id == data_dict[check_key]:
                    return instance
