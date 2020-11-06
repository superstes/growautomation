# helper functions for factory

SUPPLY_MEMBER_KEY = 'member'
SUPPLY_GROUPTYPE_KEY = 'grouptype'
SUPPLY_SETTING_KEY = 'setting'
SUPPLY_MEMBER_CONDITION_GROUP_SUBLIST = ['member', 'output']

BLUEPRINT_GROUP_KEY = 'model'  # for device-models, generic core-models and condition-groups
BLUEPRINT_OBJECT_KEY = 'object'  # for device-, core and condition-link objects
BLUEPRINT_SETTING_KEY = 'setting'  # for single-condition objects

FACTORY_OBJECT_KEY = 'object'
FACTORY_GROUP_KEY = 'group'
FACTORY_MEMBER_KEY = 'member_list'
FACTORY_CONDITION_MEMBER_KEY = 'member_dict'
FACTORY_CONDITION_SINGLE_KEY = 'condition'
FACTORY_CONDITION_GROUP_KEY = 'condition_group'
FACTORY_CONDITION_LINK_KEY = 'condition_link'
FACTORY_SETTING_KEY = 'setting_dict'


def add_instance(object_dict, obj_type, instance):
    if obj_type in object_dict:
        object_dict[obj_type].append(instance)
    else:
        object_dict[obj_type] = [instance]

    return object_dict
