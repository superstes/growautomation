# handles creation of condition link instances

from core.factory import config
from core.utils.debug import log


class Go:
    def __init__(self, blueprint, supply_list: list):
        self.blueprint = blueprint
        self.supply_list = supply_list
        self.key_member = config.SUPPLY_KEY_MEMBER_DICT

    def get(self):
        output_list = []
        log(f'Building condition link objects', level=8)

        for data_dict in self.supply_list:
            instance = self.blueprint(
                condition_match_dict=data_dict[self.key_member][config.SUPPLY_CL_KEY_MEMBER_CM],
                condition_group_dict=data_dict[self.key_member][config.SUPPLY_CL_KEY_MEMBER_CG],
                setting_dict=data_dict[config.SUPPLY_KEY_SETTING_DICT],
                object_id=data_dict[config.DB_ALL_KEY_ID],
                name=data_dict[config.DB_ALL_KEY_NAME],
            )

            output_list.append(instance)

        return output_list
