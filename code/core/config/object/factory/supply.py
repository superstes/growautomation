# prepares data for factory
#  gets db connection data from config file object
#  gets information on what to load from load module
#  loads data from db

from core.config.object.data.db import GaDataDb
from core.config.db.template import SUPPLY_DICT


class Go:
    def __init__(self):
        # loading data from db
        self.database = GaDataDb()

        self.raw_object_lot = self.database.get(SUPPLY_DICT['object']['command'])
        self.raw_group_lot = self.database.get(SUPPLY_DICT['group']['command'])
        self.raw_object_member_lot = self.database.get(SUPPLY_DICT['member']['object']['command'])
        # self.raw_setting_member_lot = database.get(SUPPLY_DICT['member']['setting']['command'])
        self.raw_grouptype_list = self.database.get(SUPPLY_DICT['grouptype']['command'])

    def get(self) -> tuple:
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

        self.database.disconnect()

        return object_dict, group_dict, grouptype_dict

    def _converter_lot_list(self, lot: list, reference_list: list) -> list:
        # converts list of tuples to list of dicts
        data_dict_list = []

        for tup in lot:
            data_dict_list.append(dict(zip(reference_list, tup)))

        return data_dict_list

    def _filter_dict(self, data_dict: dict, key_list: list) -> dict:
        new_dict = {}

        for key in key_list:
            if key in data_dict:
                new_dict[key] = data_dict[key]

        return new_dict

    def _get_obj_member_list(self, group_id: str) -> list:
        object_member_dict_list = self._converter_lot_list(
            lot=self.raw_object_member_lot, reference_list=SUPPLY_DICT['member']['object']['key_list'])

        obj_member_list = []
        group_id_key = SUPPLY_DICT['group']['id_key']

        for member_dict in object_member_dict_list:
            if member_dict[group_id_key] == group_id:
                obj_member_list.append(member_dict[group_id_key])

        return obj_member_list

    @staticmethod
    def _get_full_key_list(obj_type: str) -> list:
        if 'set_key_list' in SUPPLY_DICT[obj_type]:
            return SUPPLY_DICT[obj_type]['obj_key_list'] + SUPPLY_DICT[obj_type]['set_key_list']
        else:
            return SUPPLY_DICT[obj_type]['obj_key_list']

    @staticmethod
    def _correct_typing(raw_set_dict: dict) -> dict:
        # set right types for booleans and integers
        value_type = raw_set_dict[SUPPLY_DICT['setting']['valuetype_key']]

        value_type_bool = SUPPLY_DICT['setting']['value_type_bool']
        value_type_int = SUPPLY_DICT['setting']['value_type_int']

        key = raw_set_dict[SUPPLY_DICT['setting']['key_key']]

        try:
            if value_type == value_type_bool:
                value = bool(int(raw_set_dict[SUPPLY_DICT['setting']['value_key']]))
            elif value_type == value_type_int:
                value = int(raw_set_dict[SUPPLY_DICT['setting']['value_key']])
            else:
                raise ValueError
        except ValueError:
            value = raw_set_dict[SUPPLY_DICT['setting']['value_key']]

        return {key: value}

    def _prepare_data(self, raw_lot: list, obj_type: str) -> dict:
        # debug output raw lot

        # creates config-dict for all objects
        #   {
        #     ObjectId :
        #       {
        #          member_list: list,
        #          setting_list:
        #            [
        #              {SettingId: 1, Key: hello, Data: void},
        #              {SettingId: 2, Key: nope, Data: ok}
        #            ]
        #       }
        #   }

        if 'set_key_list' in SUPPLY_DICT[obj_type]:
            has_setting = True
        else:
            has_setting = False

        raw_dict_list = self._converter_lot_list(lot=raw_lot, reference_list=self._get_full_key_list(obj_type=obj_type))
        factory_dict = {}

        for config_dict in raw_dict_list:
            id_key = SUPPLY_DICT[obj_type]['id_key']
            map_id = config_dict[id_key]

            config_dict.pop(id_key)

            if has_setting:
                # get setting and format it
                # { settingid : {setting: data, s2: d2} }
                raw_set_dict = self._filter_dict(data_dict=config_dict, key_list=SUPPLY_DICT[obj_type]['set_key_list'])

                set_config_dict = self._correct_typing(raw_set_dict=raw_set_dict)
                # debug output set_config_dict

            if map_id not in factory_dict:
                obj_config_dict = self._filter_dict(data_dict=config_dict, key_list=SUPPLY_DICT[obj_type]['obj_key_list'])

                if obj_type == 'group':
                    obj_config_dict['member_list'] = self._get_obj_member_list(group_id=map_id)

                if has_setting:
                    obj_config_dict['setting_dict'] = set_config_dict

                factory_dict[map_id] = obj_config_dict

            elif has_setting:
                existing_set_data_dict = factory_dict[map_id]['setting_dict']
                factory_dict[map_id]['setting_dict'] = {**existing_set_data_dict, **set_config_dict}

        return factory_dict
