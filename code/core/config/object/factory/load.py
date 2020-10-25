# configures which data to load from the db -> used for the supply

DB_NAME = 'ga'

# objects
SUPPLY_DICT = {
    'object': {
        'id_key': 'ObjectID',
        'obj_key_list': ['ObjectID', 'ObjectName', 'ObjectDescription'],
        'set_key_list': ['SettingID', 'SettingValue', 'TypeDescription', 'TypeKey', 'TypeValueID'],
        'command': "select %s.Object.ObjectID, %s.Object.ObjectName, %s.Object.ObjectDescription, "
                   "%s.ObjectSetting.SettingID, %s.ObjectSetting.SettingValue, %s.SettingType.TypeDescription, "
                   "%s.SettingType.TypeKey, %s.SettingType.TypeValueID from ((%s.ObjectSetting INNER JOIN "
                   "%s.SettingType ON %s.ObjectSetting.SettingTypeID = %s.SettingType.TypeID) INNER JOIN %s.Object ON "
                   "%s.ObjectSetting.ObjectID = %s.Object.ObjectID);"
                   "" % (DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME,
                         DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME),
    },
    'group': {
        'id_key': 'GroupID',
        'type_id_key': 'GroupTypeID',
        'obj_key_list': ['GroupID', 'GroupName', 'GroupDescription', 'GroupParent', 'GroupTypeID'],
        'set_key_list': ['SettingID', 'SettingValue', 'TypeDescription', 'TypeKey', 'TypeValueID'],
        'command': "select %s.Grp.GroupID, %s.Grp.GroupName, %s.Grp.GroupDescription, %s.Grp.GroupParent, "
                   "%s.Grp.GroupTypeID, %s.GrpSetting.SettingID, %s.GrpSetting.SettingValue, "
                   "%s.SettingType.TypeDescription, %s.SettingType.TypeKey, %s.SettingType.TypeValueID "
                   "from ((%s.GrpSetting INNER JOIN %s.SettingType ON %s.GrpSetting.SettingTypeID = "
                   "%s.SettingType.TypeID) INNER JOIN %s.Grp ON %s.GrpSetting.GroupID = %s.Grp.GroupID);"
                   "" % (DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME,
                         DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME, DB_NAME)
    },
    'member': {
        'setting': {
            'key_list': ['GroupID', 'SettingID'],
            'set_command': "select GroupID, SettingID from %s.SettingGroupMember;" % DB_NAME
        },
        'object': {
            'key_list': ['GroupID', 'ObjectID'],
            'command': "select GroupID, ObjectID from %s.ObjectGroupMember;" % DB_NAME,
        }
    },
    'grouptype': {
        'id_key': 'TypeID',
        'obj_key_list': ['TypeID', 'TypeName', 'TypeCategory', 'TypeDescription'],
        'command': "select TypeID, TypeName, TypeCategory, TypeDescription from %s.GrpType;" % DB_NAME
    },
    'setting': {
        'id_key': 'SettingID',
        'key_key': 'TypeKey',
        'value_key': 'SettingValue',
        'bool_value_type': '2',
        'valuetype_key': 'TypeValueID'
    }
}
