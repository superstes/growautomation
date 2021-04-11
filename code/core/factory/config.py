# provides configuration for factory forgery and linking
#   holds hardcoded keys that will be used throughout the process
#   config dicts on how to link members and foreign keys

# supply keys
SUPPLY_KEY_MEMBER_DICT = 'member_dict'
SUPPLY_KEY_SETTING_DICT = 'setting_dict'

SUPPLY_CG_KEY_MEMBER_OO = 'member_output_object'
SUPPLY_CG_KEY_MEMBER_OG = 'member_output_group'
SUPPLY_CG_KEY_MEMBER_CL = 'member_link'
SUPPLY_CG_KEY_MEMBER_AG = 'member_area_group'

SUPPLY_CL_KEY_MEMBER_CM = 'member_condition_match'
SUPPLY_CL_KEY_MEMBER_CG = 'member_condition_group'

SUPPLY_CM_KEY_AR = 'area_id'

SUPPLY_AR_KEY_MEMBER_CG = 'member_connection_group'
SUPPLY_AR_KEY_MEMBER_CO = 'member_connection_obj'
SUPPLY_AR_KEY_MEMBER_IG = 'member_input_group'
SUPPLY_AR_KEY_MEMBER_IO = 'member_input_obj'
SUPPLY_AR_KEY_MEMBER_OG = 'member_output_group'
SUPPLY_AR_KEY_MEMBER_OO = 'member_output_obj'

SUPPLY_GENERIC_KEY_MEMBER_NESTED = 'member_nested'
SUPPLY_GENERIC_KEY_MEMBER = 'member1'

CORE_MEMBER_ATTRIBUTE = 'member_list'
CORE_DOWNLINK_ATTRIBUTE = 'downlink'
CORE_ID_ATTRIBUTE = 'object_id'

DB_ALL_KEY_ID = 'id'
DB_ALL_KEY_NAME = 'name'
DB_ALL_KEY_DESCRIPTION = 'description'
DB_KEY_DOWNLINK = 'downlink_id'

DB_ENCRYPTED_SETTING_LIST = ['sql_secret']

# generic keys for factory output
KEY_OBJECT_CONDITION_LINK = 'object_condition_link'
KEY_OBJECT_CONDITION_MATCH = 'object_condition_match'
KEY_OBJECT_CONNECTION = 'object_connection'
KEY_OBJECT_INPUT = 'object_input'
KEY_OBJECT_OUTPUT = 'object_output'
KEY_OBJECT_CONTROLLER = 'object_controller'
KEY_OBJECT_TASK = 'object_task'
KEY_OBJECT_CONDITION_MATCH_SPECIAL = 'object_condition_specialmatch'
KEY_GROUP_CONDITION = 'group_condition'
KEY_GROUP_INPUT = 'group_input'
KEY_GROUP_OUTPUT = 'group_output'
KEY_GROUP_CONNECTION = 'group_connection'
KEY_GROUP_CONTROLLER = 'group_controller'
KEY_GROUP_AREA = 'group_area'

# members

MEMBERS = {
    KEY_OBJECT_CONDITION_LINK: {
        'condition_match_dict': KEY_OBJECT_CONDITION_MATCH,
        'condition_group_dict': KEY_GROUP_CONDITION,
    },
    KEY_GROUP_CONDITION: {
        'output_object_list': KEY_OBJECT_OUTPUT,
        'output_group_list': KEY_GROUP_OUTPUT,
        'area_group_list': KEY_GROUP_AREA,
        CORE_MEMBER_ATTRIBUTE: KEY_OBJECT_CONDITION_LINK,
    },
    KEY_GROUP_INPUT: {
        CORE_MEMBER_ATTRIBUTE: KEY_OBJECT_INPUT,
    },
    KEY_GROUP_OUTPUT: {
        CORE_MEMBER_ATTRIBUTE: KEY_OBJECT_OUTPUT,
    },
    KEY_GROUP_CONNECTION: {
        CORE_MEMBER_ATTRIBUTE: KEY_OBJECT_CONNECTION,
    },
    KEY_GROUP_AREA: {
        'connection_group_list': KEY_GROUP_CONNECTION,
        'connection_obj_list': KEY_OBJECT_CONNECTION,
        'input_group_list': KEY_GROUP_INPUT,
        'input_obj_list': KEY_OBJECT_INPUT,
        'output_group_list': KEY_GROUP_OUTPUT,
        'output_obj_list': KEY_OBJECT_OUTPUT,
        'nested_list': KEY_GROUP_AREA,
    },
}

# one to one links (foreign keys)
#  must be executed after member-assignment
LINK_KEY_SEARCH_KEY = 'search_key'
LINK_KEY_SEARCH_ATTR = 'search_attr'
LINK_KEY_SET_ATTR = 'set_attr'
LINK_KEY_SET_ATTR_PARENT = 'parent_instance'

LINKS = {
    KEY_OBJECT_INPUT: {
        CORE_ID_ATTRIBUTE: {
            LINK_KEY_SEARCH_KEY: KEY_GROUP_INPUT,
            LINK_KEY_SEARCH_ATTR: CORE_MEMBER_ATTRIBUTE,
            LINK_KEY_SET_ATTR: LINK_KEY_SET_ATTR_PARENT
        },
        CORE_DOWNLINK_ATTRIBUTE: KEY_OBJECT_CONNECTION,
    },
    KEY_OBJECT_OUTPUT: {
        CORE_ID_ATTRIBUTE: {
            LINK_KEY_SEARCH_KEY: KEY_GROUP_OUTPUT,
            LINK_KEY_SEARCH_ATTR: CORE_MEMBER_ATTRIBUTE,
            LINK_KEY_SET_ATTR: LINK_KEY_SET_ATTR_PARENT
        },
        CORE_DOWNLINK_ATTRIBUTE: KEY_OBJECT_CONNECTION,
    },
    KEY_OBJECT_CONNECTION: {
        CORE_ID_ATTRIBUTE: {
            LINK_KEY_SEARCH_KEY: KEY_GROUP_CONNECTION,
            LINK_KEY_SEARCH_ATTR: CORE_MEMBER_ATTRIBUTE,
            LINK_KEY_SET_ATTR: LINK_KEY_SET_ATTR_PARENT
        },
    },
    KEY_OBJECT_CONDITION_MATCH: {
        'check_instance': [
            {LINK_KEY_SEARCH_ATTR: 'input_obj_id', LINK_KEY_SEARCH_KEY: KEY_OBJECT_INPUT},
            {LINK_KEY_SEARCH_ATTR: 'input_group_id', LINK_KEY_SEARCH_KEY: KEY_GROUP_INPUT},
            {LINK_KEY_SEARCH_ATTR: 'special_obj_id', LINK_KEY_SEARCH_KEY: KEY_OBJECT_CONDITION_MATCH_SPECIAL},
        ]
    }
}
