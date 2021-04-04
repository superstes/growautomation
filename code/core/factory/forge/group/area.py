# creates area group instances

from core.factory import config
from core.utils.debug import Log


class Go:
    def __init__(self, factory_dict: dict, supply_list: list, blueprint):
        self.factory_dict = factory_dict
        self.supply_list = supply_list
        self.blueprint = blueprint
        self.logger = Log()

        self.key_member = config.SUPPLY_KEY_MEMBER_DICT

    def get(self) -> list:
        # {
        #     [instance_list]
        # }

        area_group_list = []
        self.logger.write(f'Building area objects', level=8)

        for data_dict in self.supply_list:
            instance = self.blueprint(
                connection_group_list=data_dict[self.key_member][config.SUPPLY_AR_KEY_MEMBER_CG],
                connection_obj_list=data_dict[self.key_member][config.SUPPLY_AR_KEY_MEMBER_CO],
                input_group_list=data_dict[self.key_member][config.SUPPLY_AR_KEY_MEMBER_IG],
                input_obj_list=data_dict[self.key_member][config.SUPPLY_AR_KEY_MEMBER_IO],
                output_group_list=data_dict[self.key_member][config.SUPPLY_AR_KEY_MEMBER_OG],
                output_obj_list=data_dict[self.key_member][config.SUPPLY_AR_KEY_MEMBER_OO],
                nested_list=data_dict[self.key_member][config.SUPPLY_GENERIC_KEY_MEMBER_NESTED],
                object_id=data_dict[config.DB_ALL_KEY_ID],
                name=data_dict[config.DB_ALL_KEY_NAME],
                description=data_dict[config.DB_ALL_KEY_DESCRIPTION],
            )

            area_group_list.append(instance)

        return area_group_list
