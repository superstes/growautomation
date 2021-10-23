from core.factory.config import *
from core.config.object.core.system import GaAgent, GaServer

# provides configuration for factory supply
#   what data to query
#   how to parse it to 'raw' data dict

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
            'base': f"SELECT * FROM {DJANGO_PROJECT}_objectconditionlinkmodel;",
            SUPPLY_CL_KEY_MEMBER_CM: f"SELECT id, created, updated, `order`, condition_id, link_id FROM {DJANGO_PROJECT}_memberconditionlinkmodel;",
            SUPPLY_CL_KEY_MEMBER_CG: f"SELECT id, created, updated, `order`, group_id, link_id FROM {DJANGO_PROJECT}_memberconditionlinkmodel;",
        },
        'fields': {
            'base': ['name', 'operator'],
            SUPPLY_CL_KEY_MEMBER_CM: ['order', 'condition_id', 'link_id'],
            SUPPLY_CL_KEY_MEMBER_CG: ['order', 'group_id', 'link_id'],
        },
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
            'base': f"SELECT * FROM {DJANGO_PROJECT}_objectconditionmodel;",
        },
        'fields': {
            'base': ['name', 'description', 'value', 'operator', 'check', 'period', 'period_data', 'area_id', 'input_group_id', 'input_obj_id', 'special_obj_id'],
        },
        'setting_fields': {
            'base': ['value', 'operator', 'check', 'period', 'period_data'],
        },
    },
    KEY_OBJECT_CONDITION_MATCH_SPECIAL: {
        'queries': {
            'base': f"SELECT * FROM {DJANGO_PROJECT}_objectspecialconditionmodel;",
        },
        'fields': {
            'base': ['name', 'description'],
        },
        'setting_fields': {},
    },
    KEY_OBJECT_CONNECTION: {
        'queries': {
            'base': f"SELECT * FROM {DJANGO_PROJECT}_objectconnectionmodel;",
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
            'base': f"SELECT * FROM {DJANGO_PROJECT}_objectinputmodel;",
        },
        'fields': {
            'base': ['name', 'description', 'enabled', 'connection', 'timer', 'downlink_id'],
        },
        'setting_fields': {
            'base': ['enabled', 'connection', 'timer'],
        },
    },
    KEY_OBJECT_OUTPUT: {
        'queries': {
            'base': f"SELECT * FROM {DJANGO_PROJECT}_objectoutputmodel;",
        },
        'fields': {
            'base': ['name', 'description', 'enabled', 'connection', 'downlink_id', 'reverse_condition_id'],
        },
        'setting_fields': {
            'base': ['enabled', 'connection'],
        },
    },
    KEY_OBJECT_SERVER: {
        'queries': {
            'base': f"SELECT * FROM {DJANGO_PROJECT}_systemservermodel;",
        },
        'fields': {
            'base': GaServer.setting_list,
        },
        'setting_fields': {
            'base': GaServer.setting_list,
        },
    },
    KEY_OBJECT_AGENT: {
        'queries': {
            'base': f"SELECT * FROM {DJANGO_PROJECT}_systemagentmodel;",
        },
        'fields': {
            'base': GaAgent.setting_list,
        },
        'setting_fields': {
            'base': GaAgent.setting_list,
        },
    },
    KEY_OBJECT_TASK: {
        'queries': {
            'base': f"SELECT * FROM {DJANGO_PROJECT}_objecttaskmodel;",
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
            'base': f"SELECT * FROM {DJANGO_PROJECT}_groupconnectionmodel;",
            'member1': f"SELECT * FROM {DJANGO_PROJECT}_memberconnectionmodel;",
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
            'base': f"SELECT * FROM {DJANGO_PROJECT}_groupinputmodel;",
            'member1': f"SELECT * FROM {DJANGO_PROJECT}_memberinputmodel;",
        },
        'fields': {
            'base': ['name', 'description', 'enabled', 'script', 'script_bin', 'script_arg', 'unit', 'timer', 'datatype'],
            'member1': ['group_id', 'obj_id'],
        },
        'setting_fields': {
            'base': ['enabled', 'script', 'script_bin', 'script_arg', 'unit', 'timer', 'datatype'],
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
            'base': f"SELECT * FROM {DJANGO_PROJECT}_groupoutputmodel;",
            'member1': f"SELECT * FROM {DJANGO_PROJECT}_memberoutputmodel;",
        },
        'fields': {
            'base': ['name', 'description', 'enabled', 'script', 'script_bin', 'script_arg', 'reverse', 'reverse_type', 'reverse_type_data',
                     'reverse_script', 'reverse_script_bin', 'reverse_script_arg', 'reverse_condition_id'],  # todo: condition linking => Ticket#11
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
            'base': f"SELECT * FROM {DJANGO_PROJECT}_groupconditionmodel;",
            SUPPLY_CG_KEY_MEMBER_CL: f"SELECT * FROM {DJANGO_PROJECT}_memberconditionmodel;",
            SUPPLY_CG_KEY_MEMBER_OO: f"SELECT * FROM {DJANGO_PROJECT}_memberconditionoutputmodel;",
            SUPPLY_CG_KEY_MEMBER_OG: f"SELECT * FROM {DJANGO_PROJECT}_memberconditionoutputgroupmodel;",
            SUPPLY_CG_KEY_MEMBER_AG: f"SELECT * FROM {DJANGO_PROJECT}_memberconditionareagroupmodel;",
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
            'base': f"SELECT * FROM {DJANGO_PROJECT}_groupareamodel;",
            SUPPLY_AR_KEY_MEMBER_CG: f"SELECT id, created, updated, area_id, connection_group_id FROM {DJANGO_PROJECT}_memberareamodel;",
            SUPPLY_AR_KEY_MEMBER_CO: f"SELECT id, created, updated, area_id, connection_obj_id FROM {DJANGO_PROJECT}_memberareamodel;",
            SUPPLY_AR_KEY_MEMBER_IG: f"SELECT id, created, updated, area_id, input_group_id FROM {DJANGO_PROJECT}_memberareamodel;",
            SUPPLY_AR_KEY_MEMBER_IO: f"SELECT id, created, updated, area_id, input_obj_id FROM {DJANGO_PROJECT}_memberareamodel;",
            SUPPLY_AR_KEY_MEMBER_OG: f"SELECT id, created, updated, area_id, output_group_id FROM {DJANGO_PROJECT}_memberareamodel;",
            SUPPLY_AR_KEY_MEMBER_OO: f"SELECT id, created, updated, area_id, output_obj_id FROM {DJANGO_PROJECT}_memberareamodel;",
            SUPPLY_GENERIC_KEY_MEMBER_NESTED: f"SELECT * FROM {DJANGO_PROJECT}_nestedareamodel;",
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
