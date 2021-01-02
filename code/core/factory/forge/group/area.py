# creates area group instances

from core.factory import config
from core.factory.forge.member import Go as Member


class Go:
    def __init__(self, factory_dict: dict, supply_list: list, blueprint):
        self.factory_dict = factory_dict
        self.supply_list = supply_list
        self.blueprint = blueprint

        self.key_id = config.DB_ALL_KEY_ID
        self.key_name = config.DB_ALL_KEY_NAME
        self.key_desc = config.DB_ALL_KEY_DESCRIPTION
        self.key_member = config.SUPPLY_KEY_MEMBER_DICT

        self.key_member_cg = config.SUPPLY_AR_KEY_MEMBER_CG
        self.key_member_co = config.SUPPLY_AR_KEY_MEMBER_CO
        self.key_member_ig = config.SUPPLY_AR_KEY_MEMBER_IG
        self.key_member_io = config.SUPPLY_AR_KEY_MEMBER_IO
        self.key_member_og = config.SUPPLY_AR_KEY_MEMBER_OG
        self.key_member_oo = config.SUPPLY_AR_KEY_MEMBER_OO
        self.key_member_nested = config.SUPPLY_GENERIC_KEY_MEMBER_NESTED

    def get(self) -> list:
        # {
        #     [instance_list]
        # }

        area_group_list = []

        for data_dict in self.supply_list:
            instance = self.blueprint(
                connection_group_list=data_dict[self.key_member][self.key_member_cg],
                connection_obj_list=data_dict[self.key_member][self.key_member_co],
                input_group_list=data_dict[self.key_member][self.key_member_ig],
                input_obj_list=data_dict[self.key_member][self.key_member_io],
                output_group_list=data_dict[self.key_member][self.key_member_og],
                output_obj_list=data_dict[self.key_member][self.key_member_oo],
                nested_list=data_dict[self.key_member][self.key_member_nested],
                object_id=data_dict[self.key_id],
                name=data_dict[self.key_name],
                description=data_dict[self.key_desc],
            )

            area_group_list.append(instance)

        area_group_list = Member(
            object_list=area_group_list,
            member_list=self.factory_dict[config.KEY_GROUP_CONNECTION],
            member_attribute='connection_group_list',
        ).add()

        area_group_list = Member(
            object_list=area_group_list,
            member_list=self.factory_dict[config.KEY_OBJECT_CONNECTION],
            member_attribute='connection_obj_list',
        ).add()

        area_group_list = Member(
            object_list=area_group_list,
            member_list=self.factory_dict[config.KEY_GROUP_INPUT],
            member_attribute='input_group_list',
        ).add()

        area_group_list = Member(
            object_list=area_group_list,
            member_list=self.factory_dict[config.KEY_OBJECT_INPUT],
            member_attribute='input_obj_list',
        ).add()

        area_group_list = Member(
            object_list=area_group_list,
            member_list=self.factory_dict[config.KEY_GROUP_OUTPUT],
            member_attribute='output_group_list',
        ).add()

        area_group_list = Member(
            object_list=area_group_list,
            member_list=self.factory_dict[config.KEY_OBJECT_OUTPUT],
            member_attribute='output_obj_list',
        ).add()

        area_group_list = Member(
            object_list=area_group_list,
            member_list=area_group_list,
            member_attribute='nested_list',
        ).add()

        return area_group_list
