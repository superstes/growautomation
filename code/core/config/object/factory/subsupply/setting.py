# supplies settings for objects

from core.utils.debug import debugger
from core.config.object.factory.helper import factory as factory_helper
from core.config.object.factory.helper import supply as helper
from core.config.db.template import SUPPLY_DICT


class Go:
    SETTING_KEY_LIST = SUPPLY_DICT[factory_helper.SUPPLY_SETTING_KEY]['filtered_key_list']
    SETTING_VALUE_KEY = SUPPLY_DICT[factory_helper.SUPPLY_SETTING_KEY]['value_key']
    SETTING_VALUE_TYPE = SUPPLY_DICT[factory_helper.SUPPLY_SETTING_KEY]['valuetype_key']
    SETTING_KEY_KEY = SUPPLY_DICT[factory_helper.SUPPLY_SETTING_KEY]['key_key']

    SETTING_TYPE_BOOL = SUPPLY_DICT[factory_helper.SUPPLY_SETTING_KEY]['value_type_bool']
    SETTING_TYPE_INT = SUPPLY_DICT[factory_helper.SUPPLY_SETTING_KEY]['value_type_int']
    
    def __init__(self, data_dict_list: list, map_id: int):
        self.data_dict_list = data_dict_list
        self.map_id = map_id
    
    def get(self) -> dict:
        # setting_dict: {
        #     setting1: value1,
        #     setting2: value2
        # }

        output_dict = {}

        for setting_dict in self.data_dict_list:
            raw_set_dict = helper.filter_dict(
                data_dict=setting_dict,
                key_list=self.SETTING_KEY_LIST
            )

            set_config_dict = self._correct_types(raw_set_dict=raw_set_dict)

            output_dict.update(set_config_dict)

        return output_dict

    def _correct_types(self, raw_set_dict: dict) -> dict:
        # set right types for booleans and integers
        value_type = raw_set_dict[self.SETTING_VALUE_TYPE]

        value_type_bool = self.SETTING_TYPE_BOOL
        value_type_int = self.SETTING_TYPE_INT

        key = raw_set_dict[self.SETTING_KEY_KEY]

        try:
            if value_type == value_type_bool:
                value = bool(int(raw_set_dict[self.SETTING_VALUE_KEY]))
            elif value_type == value_type_int:
                value = int(raw_set_dict[self.SETTING_VALUE_KEY])
            else:
                raise ValueError
        except ValueError:
            value = raw_set_dict[self.SETTING_VALUE_KEY]

        return {key: value}
