# prepares data for factory
#  gets db connection data from config file object
#  loads data from db

from core.config.object.data.file import GaDataFile
from core.config.object.data.db import GaDataDb


DB_NAME = 'ga'

# objects
OBJECT_ID_ARG = 'ObjectID'
OBJECT_ARG_LIST = ['SettingID', 'ObjectID', 'SettingValue', 'ObjectName', 'ObjectDescription', 'TypeDescription',
                   'TypeKey']
LOAD_OBJECT_COMMAND = "select %s.ObjectSetting.SettingID, %s.ObjectSetting.ObjectID, %s.ObjectSetting.SettingValue, " \
                      "%s.Object.ObjectName, %s.Object.ObjectDescription, %s.SettingType.TypeDescription, " \
                      "%s.SettingType.TypeKey from ((%s.ObjectSetting INNER JOIN %s.SettingType ON " \
                      "%s.ObjectSetting.SettingTypeID = %s.SettingType.TypeID) INNER JOIN %s.Object ON " \
                      "%s.ObjectSetting.ObjectID = %s.Object.ObjectID);" \
                      "" % (DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME,
                            DB_NAME, DB_NAME, DB_NAME, DB_NAME)

# groups
GROUP_ID_ARG = 'GroupID'
GROUP_ARG_LIST = ['SettingID', 'GroupID', 'SettingValue', 'GroupName', 'GroupDescription', 'GroupParent',
                  'TypeDescription', 'TypeKey']
LOAD_GROUP_COMMAND = "select %s.GrpSetting.SettingID, %s.GrpSetting.GroupID, %s.GrpSetting.SettingValue, " \
                     "%s.Grp.GroupName, %s.Grp.GroupDescription, %s.Grp.GroupParent, %s.SettingType.TypeDescription, " \
                     "%s.SettingType.TypeKey from ((%s.GrpSetting INNER JOIN %s.SettingType ON " \
                     "%s.GrpSetting.SettingTypeID = %s.SettingType.TypeID) INNER JOIN %s.Grp ON " \
                     "%s.GrpSetting.GroupID = %s.Grp.GroupID);" \
                     "" % (DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME,
                           DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME)

# members
OBJECT_MEMBER_ARG_LIST = ['GroupID', 'ObjectID']
# SETTING_MEMBER_ARG_LIST = ['GroupID', 'SettingID']
LOAD_OBJECT_MEMBER_COMMAND = "select GroupID, ObjectID from %s.ObjectGroupMember;" % DB_NAME
# LOAD_SETTING_MEMBER_COMMAND = "select GroupID, SettingID from %s.SettingGroupMember;" % DB_NAME

# group types
GROUPTYPE_ID_ARG = 'TypeID'
GROUPTYPE_ARG_LIST = ['TypeID', 'TypeName', 'TypeCategory', 'TypeDescription']
LOAD_GRP_TYPE_COMMAND = "select TypeID, TypeName, TypeCategory, TypeDescription from %s.GrpType;" % DB_NAME


# loading data from db
database = GaDataDb(GaDataFile().get())

raw_object_lot = database.get(LOAD_OBJECT_COMMAND)
raw_group_lot = database.get(LOAD_GROUP_COMMAND)
raw_object_member_lot = database.get(LOAD_OBJECT_MEMBER_COMMAND)
# raw_setting_member_lot = database.get(LOAD_SETTING_MEMBER_COMMAND)
raw_group_type_list = database.get(LOAD_GRP_TYPE_COMMAND)


def _converter_lot_list(lot: list, reference_list: list) -> list:
    data_dict_list = []

    for tup in lot:
        data_dict_list.append(dict(zip(reference_list, tup)))

    return data_dict_list


def _prepare(raw_lot: list, reference_list: list, id_arg: str) -> dict:
    _dict_list = _converter_lot_list(lot=raw_lot, reference_list=reference_list)
    if id_arg == GROUP_ID_ARG:
        object_member_dict_list = _converter_lot_list(lot=raw_object_member_lot, reference_list=OBJECT_MEMBER_ARG_LIST)

    factory_dict = {}

    for _dict in _dict_list:
        _id = _dict[id_arg]
        _dict.pop(id_arg)
        if id_arg == GROUP_ID_ARG:
            obj_member_list = []

            for member_dict in object_member_dict_list:
                if member_dict[GROUP_ID_ARG] == _id:
                    obj_member_list.append(member_dict[GROUP_ID_ARG])

            if len(obj_member_list) > 0:
                _dict['member_list'] = obj_member_list

        factory_dict[_id] = _dict

    return factory_dict


def get() -> tuple:
    return _prepare(raw_lot=raw_object_lot, reference_list=OBJECT_ARG_LIST, id_arg=OBJECT_ID_ARG), \
           _prepare(raw_lot=raw_group_lot, reference_list=GROUP_ARG_LIST, id_arg=GROUP_ID_ARG), \
           _prepare(raw_lot=raw_group_type_list, reference_list=GROUPTYPE_ARG_LIST, id_arg=GROUPTYPE_ID_ARG)


# if __name__ == '__main__':
#     _test = get()
#     print("%s\n\n%s\n\n%s" % (_test[0], _test[1], _test[2]))
