from core.factory.config import *


DJANGO_PROJECT = 'ga'

supply_sql_dict = {
    '*': {
        'fields': {
            '*': ['id', 'created', 'updated']
          }
    },
    # OBJECTS
    KEY_OBJECT_CONDITION_LINK: {
        'queries': {
            'base': "SELECT * FROM %s_objectconditionlinkmodel;" % DJANGO_PROJECT,
            SUPPLY_CL_KEY_MEMBER_CM: "SELECT id, created, updated, `order`, condition_id, link_id FROM %s_memberconditionlinkmodel;" % DJANGO_PROJECT,
            SUPPLY_CL_KEY_MEMBER_CG: "SELECT id, created, updated, `order`, group_id, link_id FROM %s_memberconditionlinkmodel;" % DJANGO_PROJECT,
        },
        'fields': {
            'base': ['name', 'operator'],
            SUPPLY_CL_KEY_MEMBER_CM: ['order', 'condition_id', 'link_id'],
            SUPPLY_CL_KEY_MEMBER_CG: ['order', 'group_id', 'link_id'],
        },
        # 'optional_fields': {
        #     'member': ['condition_id', 'group_id']
        # },
        'setting_fields': {
            'base': ['operator'],
            SUPPLY_CL_KEY_MEMBER_CM: ['order'],
            SUPPLY_CL_KEY_MEMBER_CG: ['order'],
        },
        'member': {
            SUPPLY_CL_KEY_MEMBER_CM: {
                'group': 'link_id',
                'member': 'condition_id'
            },
            SUPPLY_CL_KEY_MEMBER_CG: {
                'group': 'link_id',
                'member': 'group_id'
            }
        },
    },
    KEY_OBJECT_CONDITION_MATCH: {
        'queries': {
            'base': "SELECT * FROM %s_objectconditionmodel;" % DJANGO_PROJECT,
        },
        'fields': {
            'base': ['name', 'description', 'value', 'operator', 'check', 'period', 'period_data', 'special', 'input_group_id', 'input_obj_id'],
        },
        # 'optional_fields': {
        #     'member': ['input_group_id', 'input_obj_id']
        # },
        'setting_fields': {
            'base': ['value', 'operator', 'check', 'period', 'period_data', 'special'],
        },
    },
    KEY_OBJECT_CONNECTION: {
        'queries': {
            'base': "SELECT * FROM %s_objectconnectionmodel;" % DJANGO_PROJECT,
        },
        'fields': {
            'base': ['name', 'description', 'enabled', 'connection'],
        },
        'setting_fields': {
            'base': ['enabled', 'connection'],
        },
    },
    KEY_OBJECT_INPUT: {
        'queries': {
            'base': "SELECT * FROM %s_objectinputmodel;" % DJANGO_PROJECT,
        },
        'fields': {
            'base': ['name', 'description', 'enabled', 'connection', 'downlink', 'timer'],
        },
        'setting_fields': {
            'base': ['enabled', 'connection', 'timer'],
        },
    },
    KEY_OBJECT_OUTPUT: {
        'queries': {
            'base': "SELECT * FROM %s_objectoutputmodel;" % DJANGO_PROJECT,
        },
        'fields': {
            'base': ['name', 'description', 'enabled', 'connection', 'downlink'],
        },
        'setting_fields': {
            'base': ['enabled', 'connection'],
        },
    },
    KEY_OBJECT_CONTROLLER: {
        'queries': {
            'base': "SELECT * FROM %s_objectcontrollermodel;" % DJANGO_PROJECT,
        },
        'fields': {
            'base': ['name', 'description', 'path_root', 'path_log', 'path_backup', 'sql_server', 'sql_port', 'sql_user', 'sql_secret', 'sql_database',
                     'log_level', 'debug', 'security', 'backup', 'timezone'],
        },
        'setting_fields': {
            'base': ['path_root', 'path_log', 'path_backup', 'sql_server', 'sql_port', 'sql_user', 'sql_secret', 'sql_database',
                     'log_level', 'debug', 'security', 'backup', 'timezone'],
        },
    },
    KEY_OBJECT_TIMER: {
        'queries': {
            'base': "SELECT * FROM %s_objecttimermodel;" % DJANGO_PROJECT,
        },
        'fields': {
            'base': ['name', 'description', 'enabled', 'timer', 'target', 'interval'],
        },
        'setting_fields': {
            'base': ['timer', 'enabled', 'target', 'interval'],
        },
    },
    # GROUPS
    KEY_GROUP_CONNECTION: {
        'queries': {
            'base': "SELECT * FROM %s_groupconnectionmodel;" % DJANGO_PROJECT,
            'member1': "SELECT * FROM %s_memberconnectionmodel;" % DJANGO_PROJECT,
        },
        'fields': {
            'base': ['name', 'description', 'enabled', 'script', 'script_bin', 'script_arg'],
            'member1': ['group_id', 'obj_id'],
        },
        'setting_fields': {
            'base': ['enabled', 'script', 'script_bin', 'script_arg'],
        },
        'member': {
            'member1': {
                'group': 'group_id',
                'member': 'obj_id'
            },
        },
    },
    KEY_GROUP_INPUT: {
        'queries': {
            'base': "SELECT * FROM %s_groupinputmodel;" % DJANGO_PROJECT,
            'member1': "SELECT * FROM %s_memberinputmodel;" % DJANGO_PROJECT,
        },
        'fields': {
            'base': ['name', 'description', 'enabled', 'script', 'script_bin', 'script_arg', 'unit', 'datatype', 'timer'],
            'member1': ['group_id', 'obj_id'],
        },
        'setting_fields': {
            'base': ['enabled', 'script', 'script_bin', 'script_arg', 'unit', 'datatype', 'timer'],
        },
        'member': {
            'member1': {
                'group': 'group_id',
                'member': 'obj_id'
            }
        },
    },
    KEY_GROUP_OUTPUT: {
        'queries': {
            'base': "SELECT * FROM %s_groupoutputmodel;" % DJANGO_PROJECT,
            'member1': "SELECT * FROM %s_memberoutputmodel;" % DJANGO_PROJECT,
        },
        'fields': {
            'base': ['name', 'description', 'enabled', 'script', 'script_bin', 'script_arg', 'reverse', 'reverse_type', 'reverse_type_data',
                     'reverse_script', 'reverse_script_bin', 'reverse_script_arg'],
            'member1': ['group_id', 'obj_id'],
        },
        'setting_fields': {
            'base': ['enabled', 'script', 'script_bin', 'script_arg', 'reverse', 'reverse_type', 'reverse_type_data',
                     'reverse_script', 'reverse_script_bin', 'reverse_script_arg'],
        },
        'member': {
            'member1': {
                'group': 'group_id',
                'member': 'obj_id'
            }
        },
    },
    KEY_GROUP_CONDITION: {
        'queries': {
            'base': "SELECT * FROM %s_groupconditionmodel;" % DJANGO_PROJECT,
            SUPPLY_CG_KEY_MEMBER_CL: "SELECT * FROM %s_memberconditionmodel;" % DJANGO_PROJECT,
            SUPPLY_CG_KEY_MEMBER_OO: "SELECT * FROM %s_memberconditionoutputmodel;" % DJANGO_PROJECT,
            SUPPLY_CG_KEY_MEMBER_OG: "SELECT * FROM %s_memberconditionoutputgroupmodel;" % DJANGO_PROJECT,
            SUPPLY_CG_KEY_MEMBER_AG: "SELECT * FROM %s_memberconditionareagroupmodel;" % DJANGO_PROJECT,
        },
        'fields': {
            'base': ['name', 'description', 'enabled', 'timer'],
            SUPPLY_CG_KEY_MEMBER_CL: ['group_id', 'link_id'],
            SUPPLY_CG_KEY_MEMBER_OO: ['condition_group_id', 'obj_id'],
            SUPPLY_CG_KEY_MEMBER_OG: ['condition_group_id', 'group_id'],
            SUPPLY_CG_KEY_MEMBER_AG: ['condition_group_id', 'group_id'],
        },
        'setting_fields': {
            'base': ['enabled', 'timer'],
        },
        'member': {
            SUPPLY_CG_KEY_MEMBER_CL: {
                'group': 'group_id',
                'member': 'link_id'
            },
            SUPPLY_CG_KEY_MEMBER_OO: {
                'group': 'condition_group_id',
                'member': 'obj_id'
            },
            SUPPLY_CG_KEY_MEMBER_OG: {
                'group': 'condition_group_id',
                'member': 'group_id'
            },
            SUPPLY_CG_KEY_MEMBER_AG: {
                'group': 'condition_group_id',
                'member': 'group_id'
            },
        },
    },
    KEY_GROUP_AREA: {
        'queries': {
            'base': "SELECT * FROM %s_groupareamodel;" % DJANGO_PROJECT,
            SUPPLY_AR_KEY_MEMBER_CG: "SELECT id, created, updated, area_id, connection_group_id FROM %s_memberareamodel;" % DJANGO_PROJECT,
            SUPPLY_AR_KEY_MEMBER_CO: "SELECT id, created, updated, area_id, connection_obj_id FROM %s_memberareamodel;" % DJANGO_PROJECT,
            SUPPLY_AR_KEY_MEMBER_IG: "SELECT id, created, updated, area_id, input_group_id FROM %s_memberareamodel;" % DJANGO_PROJECT,
            SUPPLY_AR_KEY_MEMBER_IO: "SELECT id, created, updated, area_id, input_obj_id FROM %s_memberareamodel;" % DJANGO_PROJECT,
            SUPPLY_AR_KEY_MEMBER_OG: "SELECT id, created, updated, area_id, output_group_id FROM %s_memberareamodel;" % DJANGO_PROJECT,
            SUPPLY_AR_KEY_MEMBER_OO: "SELECT id, created, updated, area_id, output_obj_id FROM %s_memberareamodel;" % DJANGO_PROJECT,
            SUPPLY_GENERIC_KEY_MEMBER_NESTED: "SELECT * FROM %s_nestedareamodel;" % DJANGO_PROJECT,
        },
        'fields': {
            'base': ['name', 'description'],
            SUPPLY_AR_KEY_MEMBER_CG: ['area_id', 'connection_group_id'],
            SUPPLY_AR_KEY_MEMBER_CO: ['area_id', 'connection_obj_id'],
            SUPPLY_AR_KEY_MEMBER_IG: ['area_id', 'input_group_id'],
            SUPPLY_AR_KEY_MEMBER_IO: ['area_id', 'input_obj_id'],
            SUPPLY_AR_KEY_MEMBER_OG: ['area_id', 'output_group_id'],
            SUPPLY_AR_KEY_MEMBER_OO: ['area_id', 'output_obj_id'],
            SUPPLY_GENERIC_KEY_MEMBER_NESTED: ['group_id', 'nested_group_id'],
        },
        'setting_fields': {},
        'member': {
            SUPPLY_AR_KEY_MEMBER_CG: {
                'group': 'area_id',
                'member': 'connection_group_id'
            },
            SUPPLY_AR_KEY_MEMBER_CO: {
                'group': 'area_id',
                'member': 'connection_obj_id'
            },
            SUPPLY_AR_KEY_MEMBER_IG: {
                'group': 'area_id',
                'member': 'input_group_id'
            },
            SUPPLY_AR_KEY_MEMBER_IO: {
                'group': 'area_id',
                'member': 'input_obj_id'
            },
            SUPPLY_AR_KEY_MEMBER_OG: {
                'group': 'area_id',
                'member': 'output_group_id'
            },
            SUPPLY_AR_KEY_MEMBER_OO: {
                'group': 'area_id',
                'member': 'output_obj_id'
            },
            SUPPLY_GENERIC_KEY_MEMBER_NESTED: {
                'group': 'group_id',
                'member': 'nested_group_id'
            },
        },
    },
}
