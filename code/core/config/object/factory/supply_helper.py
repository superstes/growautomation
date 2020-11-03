# helper functions for supply

from core.config.db.template import SUPPLY_DICT


def converter_lot_list(lot: list, reference_list: list) -> list:
    # converts list of tuples to list of dicts
    data_dict_list = []

    for tup in lot:
        data_dict_list.append(dict(zip(reference_list, tup)))

    return data_dict_list


def filter_dict(data_dict: dict, key_list: list) -> dict:
    new_dict = {}

    for key in key_list:
        if key in data_dict:
            new_dict[key] = data_dict[key]

    return new_dict


def get_full_key_list(obj_type: str) -> list:
    if 'set_key_list' in SUPPLY_DICT[obj_type]:
        return SUPPLY_DICT[obj_type]['obj_key_list'] + SUPPLY_DICT[obj_type]['set_key_list']
    else:
        return SUPPLY_DICT[obj_type]['obj_key_list']


def correct_types(raw_set_dict: dict) -> dict:
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

    # debugger("config-obj-factory-supply-helper | correct_types | type matching: '%s' '%s' before: '%s' after: '%s'"
    #          % (value_type_bool, value_type, raw_set_dict[SUPPLY_DICT['setting']['value_key']], value))

    return {key: value}


def get_obj_member_list(raw_object_member_lot: list, group_id: str) -> list:
    object_member_dict_list = converter_lot_list(
        lot=raw_object_member_lot, reference_list=SUPPLY_DICT['member']['object']['key_list'])

    obj_member_list = []
    group_id_key = SUPPLY_DICT['group']['id_key']

    for member_dict in object_member_dict_list:
        if member_dict[group_id_key] == group_id:
            obj_member_list.append(member_dict[group_id_key])

    return obj_member_list


def get_setting_dict(config_dict: dict, obj_type: str) -> dict:
    # get setting and format it
    # { settingid : {setting: data, s2: d2} }
    print("get_setting_dict: '%s'\nkeys: '%s'\nobjtype: '%s'" % (config_dict, SUPPLY_DICT[obj_type]['set_key_list'], obj_type))

    raw_set_dict = filter_dict(
        data_dict=config_dict,
        key_list=SUPPLY_DICT[obj_type]['set_key_list']
    )

    # debugger("config-obj-factory-supply-helper | get_setting_dict | set_config_dict '%s'" % set_config_dict)

    return correct_types(raw_set_dict=raw_set_dict)


def add_setting(obj_type: str, config_dict: dict, map_id: int, factory_dict: dict, obj_config_dict: dict):
    # check if the type has settings
    if 'set_key_list' in SUPPLY_DICT[obj_type]:
        has_setting = True
    else:
        has_setting = False

    if has_setting:
        # formats every setting+object/group combo for the use in the factory
        set_config_dict = get_setting_dict(
            config_dict=config_dict,
            obj_type=obj_type
        )

        if map_id not in factory_dict or 'setting_dict' not in factory_dict[map_id]:
            # add settings
            obj_config_dict['setting_dict'] = set_config_dict
            factory_dict[map_id] = obj_config_dict

        else:
            # if the object does already exist in the dict -> only add the new settings
            existing_set_data_dict = factory_dict[map_id]['setting_dict']
            factory_dict[map_id]['setting_dict'] = {**existing_set_data_dict, **set_config_dict}

    return factory_dict
