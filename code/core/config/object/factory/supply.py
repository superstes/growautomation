# prepares data for factory
#  gets db connection data from config file object
#  gets information on what to load from load module
#  loads data from db

from core.utils.debug import debugger
from core.utils.debug import Log
from core.config.object.data.db import GaDataDb
from core.config.db.template import SUPPLY_DICT
from core.config.object.factory import supply_helper as helper


class Go:
    def __init__(self):
        # loading data from db
        self.database = GaDataDb()

        self.raw_object_lot = self.database.get(SUPPLY_DICT['object']['command'])
        self.raw_group_lot = self.database.get(SUPPLY_DICT['group']['command'])
        self.raw_object_member_lot = self.database.get(SUPPLY_DICT['member']['object']['command'])
        # self.raw_setting_member_lot = database.get(SUPPLY_DICT['member']['setting']['command'])
        self.raw_grouptype_list = self.database.get(SUPPLY_DICT['grouptype']['command'])
        self.raw_condition_list = self.database.get(SUPPLY_DICT['condition']['command'])
        self.raw_condition_group_list = self.database.get(SUPPLY_DICT['condition_group']['command'])
        self.raw_condition_link_list = self.database.get(SUPPLY_DICT['condition_link']['command'])

    def get(self) -> dict:
        object_dict = self._prepare_data(
            raw_lot=self.raw_object_lot,
            obj_type='object'
        )

        group_dict = self._prepare_data(
            raw_lot=self.raw_group_lot,
            obj_type='group'
        )

        grouptype_dict = self._prepare_data(
            raw_lot=self.raw_grouptype_list,
            obj_type='grouptype'
        )

        condition_dict = self._prepare_data(
            raw_lot=self.raw_condition_list,
            obj_type='condition'
        )

        condition_group_dict = self._prepare_data_condition_group(
            raw_lot=self.raw_condition_group_list,
            obj_type='condition_group'
        )

        condition_link_dict = self._prepare_data_condition_link(
            raw_lot=self.raw_condition_link_list,
            obj_type='condition_link'
        )

        output_dict = {
            'object': object_dict,
            'group': group_dict,
            'grouptype': grouptype_dict,
            'condition': condition_dict,
            'condition_group': condition_group_dict,
            'condition_link': condition_link_dict
        }

        self.database.disconnect()

        debugger("config-obj-factory-supply | get | output object:\n'%s'\n\n" % output_dict)

        return output_dict

    def _prepare_data(self, raw_lot: list, obj_type: str) -> dict:
        # creates config-dict for all default objects:
        #   {
        #     ObjectId :
        #       {
        #          member_list: list,  -> only if the type is group
        #          setting_dict: {  -> only if the type has settings
        #              setting1: value1,
        #              setting2: value2
        #          }
        #       }
        #   }

        id_key = SUPPLY_DICT[obj_type]['id_key']
        key_list = SUPPLY_DICT[obj_type]['obj_key_list']

        # check if the type has settings
        if 'set_key_list' in SUPPLY_DICT[obj_type]:
            has_setting = True
        else:
            has_setting = False

        # create a data dict from the database-output-tuple-list and keywords
        raw_dict_list = helper.converter_lot_list(
            lot=raw_lot,
            reference_list=helper.get_full_key_list(obj_type=obj_type)
        )
        factory_dict = {}

        # formats every dataset received from the db for the use in the factory
        for config_dict in raw_dict_list:
            map_id = int(config_dict[id_key])

            config_dict.pop(id_key)

            if has_setting:
                # formats every setting+object/group combo for the use in the factory
                set_config_dict = helper.get_setting_dict(
                    config_dict=config_dict,
                    obj_type=obj_type
                )

            if map_id not in factory_dict:
                # if the object doesn't already exist in the dict -> initialize it

                obj_config_dict = helper.filter_dict(
                    data_dict=config_dict,
                    key_list=key_list
                )

                if obj_type == 'group':
                    # add members to groups

                    obj_config_dict['member_list'] = self._get_member_list(map_id=map_id)

                if has_setting:
                    # add settings
                    obj_config_dict['setting_dict'] = set_config_dict

                factory_dict[map_id] = obj_config_dict

            elif has_setting:
                # if the object does already exist in the dict -> only add the new settings

                existing_set_data_dict = factory_dict[map_id]['setting_dict']
                factory_dict[map_id]['setting_dict'] = {**existing_set_data_dict, **set_config_dict}

        return factory_dict

    def _get_member_list(self, map_id):
        return helper.get_obj_member_list(
            raw_object_member_lot=self.raw_object_member_lot,
            group_id=map_id
        )

    @staticmethod
    def _prepare_data_condition_link(raw_lot: list, obj_type: str):
        # creates config-dict for condition link objects:
        #   {
        #     LinkId :
        #       {
        #          operator: op,
        #          member_dict: {
        #              group: [list],
        #              condition: [list]
        #          }
        #       }
        #   }

        id_key = SUPPLY_DICT[obj_type]['id_key']
        operator_key = SUPPLY_DICT[obj_type]['operator_key']
        member_group_key = SUPPLY_DICT[obj_type]['member_group_key']
        member_condition_key = SUPPLY_DICT[obj_type]['member_condition_key']

        raw_dict_list = helper.converter_lot_list(
            lot=raw_lot,
            reference_list=SUPPLY_DICT[obj_type]['obj_key_list']
        )

        factory_dict = {}

        for config_dict in raw_dict_list:
            map_id = int(config_dict[id_key])

            member_group = []
            member_condition = []

            if config_dict[member_group_key] is not None:
                member_group.append(int(config_dict[member_group_key]))
            else:
                member_condition.append(int(config_dict[member_condition_key]))

            member_dict = {
                member_group_key: member_group,
                member_condition_key: member_condition
            }

            if map_id not in factory_dict:
                factory_dict[map_id] = {
                    operator_key: config_dict[operator_key],
                    'member_dict': member_dict
                }
            else:
                existing_member_dict = factory_dict[map_id]['member_dict']
                factory_dict[map_id]['member_dict'] = {**existing_member_dict, **member_dict}

        return factory_dict

    @staticmethod
    def _prepare_data_condition_group(raw_lot: list, obj_type: str):
        # creates config-dict for condition group objects:
        #   {
        #     ObjectId :
        #       {
        #          member_list: list,  -> only if the type is group
        #          setting_dict: {  -> only if the type has settings
        #              setting1: value1,
        #              setting2: value2
        #          }
        #       }
        #   }

        id_key = SUPPLY_DICT[obj_type]['id_key']
        key_list = SUPPLY_DICT[obj_type]['obj_key_list']
        member_key = SUPPLY_DICT[obj_type]['member_key']

        # create a data dict from the database-output-tuple-list and keywords
        raw_dict_list = helper.converter_lot_list(
            lot=raw_lot,
            reference_list=helper.get_full_key_list(obj_type=obj_type)
        )
        factory_dict = {}

        # formats every dataset received from the db for the use in the factory
        for config_dict in raw_dict_list:
            map_id = int(config_dict[id_key])

            if map_id not in factory_dict:
                # if the object doesn't already exist in the dict -> set it

                obj_config_dict = helper.filter_dict(
                    data_dict=config_dict,
                    key_list=key_list
                )

                # add condition link-members
                obj_config_dict['member_list'] = [_[member_key] for _ in raw_dict_list if _[id_key] == map_id]

                factory_dict[map_id] = obj_config_dict

        return factory_dict
