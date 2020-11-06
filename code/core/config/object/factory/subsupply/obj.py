# supplies data for object instances

from core.utils.debug import debugger
from core.config.object.factory.helper import supply as helper
from core.config.object.factory.helper import factory as factory_helper
from core.config.object.factory.subsupply.member import Go as SupplyMember
from core.config.object.factory.subsupply.setting import Go as SupplySetting
from core.config.db.template import SUPPLY_DICT


class Go:
    SETTING_FACTORY_KEY = factory_helper.FACTORY_SETTING_KEY
    MEMBER_FACTORY_KEY = factory_helper.FACTORY_MEMBER_KEY

    def __init__(self, raw_data_lot: list, obj_type: str, member_data: dict = None, setting_data: list = None):
        self.raw_data_lot = raw_data_lot
        self.obj_type = obj_type
        self.member_data = member_data
        self.setting_data = setting_data
        self.SUPPLY_DICT = SUPPLY_DICT[obj_type]

    def get(self) -> dict:
        # creates config-dict for all default objects:
        #   {
        #     ObjectId :
        #       {
        #          member_list: list,  -> only if the type has members
        #          setting_dict: {  -> only if the type has settings
        #              setting1: value1,
        #              setting2: value2
        #          }
        #       }
        #   }

        setting_key = self.SUPPLY_DICT['set_key']
        id_key = self.SUPPLY_DICT['id_key']
        key_list = self.SUPPLY_DICT['key_list']

        has_member = self.SUPPLY_DICT['member']
        has_setting = self.SUPPLY_DICT['setting']

        if has_setting:
            # prefilter the setting data so not every iteration needs to work the whole list

            new_setting_data = []

            for setting_dict in self.setting_data:
                if setting_dict[setting_key] is not None:
                    new_setting_data.append(setting_dict)

            self.setting_data = new_setting_data

        # create a data dict from the database-output-tuple-list and keywords
        raw_dict_list = helper.converter_lot_list(
            lot=self.raw_data_lot,
            reference_list=key_list
        )
        factory_dict = {}

        # formats every dataset received from the db for the use in the factory
        for config_dict in raw_dict_list:
            map_id = int(config_dict[id_key])

            if map_id not in factory_dict:

                obj_config_dict = helper.filter_dict(
                    data_dict=config_dict,
                    key_list=key_list
                )

                if has_member:
                    # add members to groups

                    obj_config_dict[self.MEMBER_FACTORY_KEY] = SupplyMember(
                        raw_member_dict=self.member_data,
                        obj_type=self.obj_type,
                        group_id=map_id
                    ).get()

                if has_setting:
                    # add settings to obj

                    obj_config_dict[self.SETTING_FACTORY_KEY] = SupplySetting(
                        data_dict_list=self.setting_data,
                        map_id=map_id,
                        ).get()

                factory_dict[map_id] = obj_config_dict

        return factory_dict

    # def _condition_link(self):
    #     # creates config-dict for condition link objects:
    #     #   {
    #     #     LinkId :
    #     #       {
    #     #          member_dict: {
    #     #              groups: {
    #     #                 orderid: member
    #     #              },
    #     #              objects: {
    #     #                  orderid: member
    #     #              },
    #     #          }
    # 
    #     id_key = self.SUPPLY_DICT['id_key']
    # 
    #     raw_dict_list = helper.converter_lot_list(
    #         lot=self.raw_data_lot,
    #         reference_list=self.SUPPLY_DICT['obj_key_list']
    #     )
    # 
    #     factory_dict = {}
    # 
    #     for config_dict in raw_dict_list:
    #         map_id = int(config_dict[id_key])
    # 
    #         # member_group = []
    #         # member_condition = []
    #         #
    #         # if config_dict[member_group_key] is not None:
    #         #     member_group.append(int(config_dict[member_group_key]))
    #         # else:
    #         #     member_condition.append(int(config_dict[member_condition_key]))
    #         #
    #         # member_dict = {
    #         #     member_group_key: member_group,
    #         #     member_condition_key: member_condition
    #         # }
    # 
    #         if map_id not in factory_dict:
    #             factory_dict[map_id] = {
    #                 operator_key: config_dict[operator_key],
    #                 'member_dict': member_dict
    #             }
    #         else:
    #             existing_member_dict = factory_dict[map_id]['member_dict']
    #             factory_dict[map_id]['member_dict'] = {**existing_member_dict, **member_dict}
    # 
    #     return factory_dict

    # def _condition_group(self):
    #     # creates config-dict for condition group objects:
    #     # uses raw_group_lot to create setting_dict; since it has all group-settings within
    #     #   {
    #     #     ObjectId :
    #     #       {
    #     #          member_dict: {
    #     #                     subkey1: {
    #     #                             links: [list],
    #     #                             conditiongroups: [list]
    #     #                         },
    #     #                     subkey2: {
    #     #                             objects: [list],
    #     #                             groups: [list]
    #     #                         },
    #     #                 }
    #     #          setting_dict: {
    #     #              setting1: value1,
    #     #              setting2: value2
    #     #          }
    #     #       }
    #     #   }
    # 
    #     id_key = self.SUPPLY_DICT['id_key']
    #     key_list = self.SUPPLY_DICT['obj_key_list']
    # 
    #     # create a data dict from the database-output-tuple-list and keywords
    #     raw_dict_list = helper.converter_lot_list(
    #         lot=self.raw_data_lot,
    #         reference_list=helper.get_full_key_list(obj_type=self.obj_type)
    #     )
    #     raw_group_dict_list = helper.converter_lot_list(
    #         lot=self.second_raw_data_lot,
    #         reference_list=helper.get_full_key_list(obj_type='group')  # since the settings are in the group_config_dict
    #     )
    # 
    #     factory_dict = {}
    # 
    #     # formats every dataset received from the db for the use in the factory
    #     for config_dict in raw_dict_list:
    #         map_id = int(config_dict[id_key])
    # 
    #         obj_config_dict = {}
    # 
    #         if map_id not in factory_dict:
    #             # if the object doesn't already exist in the dict -> set it
    # 
    #             obj_config_dict = helper.filter_dict(
    #                 data_dict=config_dict,
    #                 key_list=key_list
    #             )
    # 
    #             # add condition link-members
    #             obj_config_dict['member_list'] = [_[member_key] for _ in raw_dict_list if _[id_key] == map_id]
    # 
    #             factory_dict[map_id] = obj_config_dict
    # 
    #             for group_config_dict in raw_group_dict_list:
    #                 if int(group_config_dict[id_key]) == map_id:
    #                     factory_dict = helper.add_setting(
    #                         obj_type='group',  # since the settings are in the group_config_dict
    #                         config_dict=group_config_dict,
    #                         map_id=map_id,
    #                         factory_dict=factory_dict,
    #                         obj_config_dict=obj_config_dict
    #                     )
    # 
    #     return factory_dict
