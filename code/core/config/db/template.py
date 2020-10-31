# sql templates used throughout the core modules

from core.config.object.data.file import GaDataFile


file_config_dict = GaDataFile().get()

DB_NAME = file_config_dict['sql_database']

# templates

SUPPLY_DICT = {
    # configures which data to load from the db -> used for the supply
    'object': {
        'id_key': 'ObjectID',
        'obj_key_list': ['ObjectID', 'ObjectName', 'ObjectDescription'],
        'set_key_list': ['SettingID', 'SettingValue', 'TypeDescription', 'TypeKey', 'TypeValueID'],
        'command': "select Object.ObjectID, Object.ObjectName, Object.ObjectDescription, "
                   "ObjectSetting.SettingID, ObjectSetting.SettingValue, SettingType.TypeDescription, "
                   "SettingType.TypeKey, SettingType.TypeValueID from ((ObjectSetting INNER JOIN "
                   "SettingType ON ObjectSetting.SettingTypeID = SettingType.TypeID) INNER JOIN Object ON "
                   "ObjectSetting.ObjectID = Object.ObjectID);",
    },
    'group': {
        'id_key': 'GroupID',
        'type_id_key': 'GroupTypeID',
        'obj_key_list': ['GroupID', 'GroupName', 'GroupDescription', 'GroupParent', 'GroupTypeID'],
        'set_key_list': ['SettingID', 'SettingValue', 'TypeDescription', 'TypeKey', 'TypeValueID'],
        'command': "select Grp.GroupID, Grp.GroupName, Grp.GroupDescription, Grp.GroupParent, "
                   "Grp.GroupTypeID, GrpSetting.SettingID, GrpSetting.SettingValue, "
                   "SettingType.TypeDescription, SettingType.TypeKey, SettingType.TypeValueID "
                   "from ((GrpSetting INNER JOIN SettingType ON GrpSetting.SettingTypeID = "
                   "SettingType.TypeID) INNER JOIN Grp ON GrpSetting.GroupID = Grp.GroupID);"
    },
    'member': {
        'setting': {
            'key_list': ['GroupID', 'SettingID'],
            'set_command': "select GroupID, SettingID from SettingGroupMember;"
        },
        'object': {
            'key_list': ['GroupID', 'ObjectID'],
            'command': "select GroupID, ObjectID from ObjectGroupMember;",
        }
    },
    'grouptype': {
        'id_key': 'TypeID',
        'obj_key_list': ['TypeID', 'TypeName', 'TypeCategory', 'TypeDescription'],
        'command': "select TypeID, TypeName, TypeCategory, TypeDescription from GrpType;"
    },
    'setting': {
        'id_key': 'SettingID',
        'key_key': 'TypeKey',
        'value_key': 'SettingValue',
        'value_type_bool': 'bool',
        'value_type_int': 'int',
        'valuetype_key': 'TypeValueID'
    }
}

DEVICE_DICT = {
    'task': "INSERT INTO TaskLog (TaskResult, TaskMessage, TaskCategory, ObjectID) "
            "VALUES ('%s','%s','%s','%s');",
    'data': "INSERT INTO InputData (ObjectID, DataValue, DataValueID) VALUES ('%s','%s','%s');",
}

DB_CHECK_DICT = {
    'read': 'SELECT * FROM ga.test LIMIT 10;',
    'write': [
        'CREATE TABLE ga.test_%s;',
        'DROP TABLE ga.test_%s;'
    ]
}
