# handles creation of condition link instances

from core.utils.debug import debugger
from core.factory import config


class Go:
    def __init__(self, blueprint, supply_list: list):
        self.blueprint = blueprint
        self.supply_list = supply_list

        self.key_id = config.DB_ALL_KEY_ID
        self.key_name = config.DB_ALL_KEY_NAME
        self.key_setting = config.SUPPLY_KEY_SETTING_DICT

        self.key_member = config.SUPPLY_KEY_MEMBER_DICT
        self.key_member_cm = config.SUPPLY_CL_KEY_MEMBER_CM
        self.key_member_cg = config.SUPPLY_CL_KEY_MEMBER_CG

    def get(self):
        output_list = []

        for data_dict in self.supply_list:
            instance = self.blueprint(
                condition_match_dict=data_dict[self.key_member][self.key_member_cm],
                condition_group_dict=data_dict[self.key_member][self.key_member_cg],
                setting_dict=data_dict[self.key_setting],
                object_id=data_dict[self.key_id],
                name=data_dict[self.key_name],
            )

            output_list.append(instance)

        return output_list
