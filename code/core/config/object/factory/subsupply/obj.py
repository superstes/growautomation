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
    MEMBER_DICT_FACTORY_KEY = factory_helper.FACTORY_CONDITION_MEMBER_KEY

    SET_KEY = 'set_key'

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

        id_key = self.SUPPLY_DICT['id_key']
        key_list = self.SUPPLY_DICT['key_list']

        has_member = self.SUPPLY_DICT['member']
        has_setting = self.SUPPLY_DICT['setting']

        if has_setting:
            setting_key = self.SUPPLY_DICT['set_key']

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

                    members = SupplyMember(
                        raw_member_dict=self.member_data,
                        obj_type=self.obj_type,
                        group_id=map_id
                    ).get()

                    if type(members) == dict:
                        member_key = self.MEMBER_DICT_FACTORY_KEY
                    else:
                        member_key = self.MEMBER_FACTORY_KEY

                    obj_config_dict[member_key] = members

                if has_setting:
                    # add settings to obj

                    obj_config_dict[self.SETTING_FACTORY_KEY] = SupplySetting(
                        data_dict_list=self.setting_data,
                        map_id=map_id,
                        set_key=self.SUPPLY_DICT[self.SET_KEY]
                        ).get()
                factory_dict[map_id] = obj_config_dict

        return factory_dict
