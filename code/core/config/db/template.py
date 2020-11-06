# sql templates used throughout the core modules

from core.config.object.data.file import GaDataFile
from core.config.object.factory.helper import factory as factory_helper


file_config_dict = GaDataFile().get()

DB_NAME = file_config_dict['sql_database']

# templates

SUPPLY_DICT = {
    # configures which data to load from the db -> used for the supply module
    factory_helper.FACTORY_OBJECT_KEY: {
        'id_key': 'ObjectID',
        # which db column is used for the object_id
        'name_key': 'ObjectName',
        'description_key': 'ObjectDescription',
        'setting': True,
        'member': False,
        'set_key': 'ObjectID',
        'key_list': ['ObjectID', 'ObjectName', 'ObjectDescription'],
        # which db columns are needed for the settings
        'command': 'select ObjectID, ObjectName, ObjectDescription from Object;',
        # command to query raw data
    },
    factory_helper.FACTORY_GROUP_KEY: {
        'id_key': 'GroupID',
        'name_key': 'GroupName',
        'description_key': 'GroupDescription',
        'parent_key': 'GroupParent',
        'type_id_key': 'GroupTypeID',
        'setting': True,
        'member': True,
        'set_key': 'GroupID',
        'key_list': ['GroupID', 'GroupName', 'GroupDescription', 'GroupParent', 'GroupTypeID'],
        'command': 'select GroupID, GroupName, GroupDescription, GroupParent, GroupTypeID from Grp;'
    },
    factory_helper.SUPPLY_MEMBER_KEY: {
        factory_helper.FACTORY_OBJECT_KEY: {
            'key_list': ['GroupID', 'ObjectID'],
            'command': "select GroupID, ObjectID from ObjectGroupMember;",
            'id_key': 'GroupID',
        },
        factory_helper.FACTORY_CONDITION_GROUP_KEY: {
            factory_helper.SUPPLY_MEMBER_CONDITION_GROUP_SUBLIST[0]: {
                'key_list': ['GroupID', 'LinkID', 'ConditionGroupID'],
                'command': 'select GroupID, LinkID, ConditionGroupID from ConditionMember;',
                'id_key': 'GroupID',
                'member_group_key': 'ConditionGroupID',
                'member_object_key': 'LinkID',
            },
            factory_helper.SUPPLY_MEMBER_CONDITION_GROUP_SUBLIST[1]: {
                'key_list': ['ConditionGroupID', 'ObjectID', 'GroupID'],
                'command': 'select ConditionGroupID, ObjectID, GroupID from ConditionOutputMember;',
                'id_key': 'ConditionGroupID',
                'member_group_key': 'GroupID',
                'member_object_key': 'ObjectID',
            }
        },
        factory_helper.FACTORY_CONDITION_LINK_KEY: {
            'key_list': ['LinkID', 'GroupID', 'ConditionID', 'OrderID'],
            'command': 'select LinkID, GroupID, ConditionID, OrderID from ConditionLinkMember;',
            'id_key': 'LinkID',
            'member_group_key': 'GroupID',
            'member_object_key': 'ConditionID',
            'member_order_key': 'OrderID',
        },
        # 'setting': {
        #     'key_list': ['GroupID', 'SettingID'],
        #     'set_command': "select GroupID, SettingID from SettingGroupMember;",
        #     'id_key': 'GroupID',
        # },
    },
    factory_helper.SUPPLY_GROUPTYPE_KEY: {
        'id_key': 'TypeID',
        'key_list': ['TypeID', 'TypeName', 'TypeCategory', 'TypeDescription'],
        'command': "select TypeID, TypeName, TypeCategory, TypeDescription from GrpType;",
        'member': False,
        'setting': False,
    },
    factory_helper.SUPPLY_SETTING_KEY: {
        'id_key': 'SettingID',
        'key_key': 'TypeKey',
        'value_key': 'SettingValue',
        'value_type_bool': 'bool',
        'value_type_int': 'int',
        'valuetype_key': 'TypeValueID',
        'key_list': ['SettingID', 'SettingValue', 'TypeDescription', 'TypeKey', 'TypeValueID', 'ObjectID', 'GroupID',
                     'ConditionGroupID', 'ConditionLinkID', 'ConditionObjectID'],
        'filtered_key_list': ['SettingID', 'SettingValue', 'TypeDescription', 'TypeKey', 'TypeValueID'],
        'command': 'select Setting.SettingID, Setting.SettingValue, SettingType.TypeDescription, SettingType.TypeKey, '
                   'SettingType.TypeValueID, Setting.ObjectID, Setting.GroupID, Setting.ConditionGroupID, '
                   'Setting.ConditionLinkID, Setting.ConditionObjectID from Setting '
                   'INNER JOIN SettingType ON Setting.SettingTypeID = SettingType.TypeID;'
    },
    factory_helper.FACTORY_CONDITION_SINGLE_KEY: {
        'id_key': 'ConditionID',
        'name_key': 'ConditionName',
        'description_key': 'ConditionDescription',
        'object_key': 'ObjectID',
        'setting': True,
        'member': False,
        'set_key': 'ConditionObjectID',
        'key_list': ['ConditionID', 'ConditionName', 'ObjectID', 'ConditionDescription'],
        'command': 'select ConditionID, ConditionName, ObjectID, ConditionDescription from ConditionObject;',
    },
    factory_helper.FACTORY_CONDITION_GROUP_KEY: {
        'id_key': 'GroupID',
        'type_id_key': 'GroupTypeID',
        'name_key': 'GroupName',
        'description_key': 'GroupDescription',
        'parent_key': 'GroupParent',
        'setting': True,
        'member': True,
        'set_key': 'ConditionGroupID',
        'key_list': ['GroupID', 'GroupName', 'GroupDescription', 'GroupParent', 'GroupTypeID'],
        'command': 'select GroupID, GroupName, GroupDescription, GroupParent, GroupTypeID from Grp;'
    },
    factory_helper.FACTORY_CONDITION_LINK_KEY: {
        'id_key': 'LinkID',
        'name_key': 'LinkName',
        'setting': True,
        'member': True,
        'set_key': 'ConditionLinkID',
        'key_list': ['LinkID', 'LinkName'],
        'command': 'select LinkID, LinkName from ConditionLink;',
    },
}

DEVICE_DICT = {
    'task': "INSERT INTO TaskLog (TaskResult, TaskMessage, TaskCategory, ObjectID) "
            "VALUES ('%s','%s','%s','%s');",
    'input': {
        'data': "INSERT INTO InputData (ObjectID, DataValue, DataValueID) VALUES ('%s','%s','%s');",
    },
    'output': {
        'data': {
            'time': "select DataValue, DataValueID from InputData where ObjectID = '%s' and created BETWEEN "
                    "TIMESTAMP('%s') and TIMESTAMP('%s') ORDER BY created DESC",
            'range': "select DataValue, DataValueID from InputData where ObjectID = '%s' ORDER BY created DESC LIMIT %s"
        }
    }
}

DB_CHECK_DICT = {
    'read': 'SELECT * FROM ga.test LIMIT 10;',
    'write': [
        'CREATE TABLE ga.test_%s;',
        'DROP TABLE ga.test_%s;'
    ]
}
