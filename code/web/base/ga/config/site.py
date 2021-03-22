from ..forms import *

GA_USER_GROUP = 'ga_user'
GA_READ_GROUP = 'ga_read'
GA_WRITE_GROUP = 'ga_write'
GA_ADMIN_GROUP = 'ga_admin'

type_dict = {
    # objects
    'connectionobject': {'model': ObjectConnectionModel, 'form': ObjectConnectionForm, 'pretty': 'Connection object', 'hidden': False},
    'inputobject': {'model': ObjectInputModel, 'form': ObjectInputForm, 'pretty': 'Input object', 'hidden': False},
    'outputobject': {'model': ObjectOutputModel, 'form': ObjectOutputForm, 'pretty': 'Output object', 'hidden': False},
    'conditionobject': {'model': ObjectConditionModel, 'form': ObjectConditionForm, 'pretty': 'Condition match', 'hidden': False},
    'conditionlinkobject': {'model': ObjectConditionLinkModel, 'form': ObjectConditionLinkForm, 'pretty': 'Condition link', 'hidden': False},
    'controllerobject': {'model': ObjectControllerModel, 'form': ObjectControllerForm, 'pretty': 'Controller', 'hidden': False},
    'timerobject': {'model': ObjectTimerModel, 'form': ObjectTimerForm, 'pretty': 'Timer', 'hidden': False},
    # groups
    'connectiongroup': {'model': GroupConnectionModel, 'form': GroupConnectionForm, 'pretty': 'Connection group', 'hidden': False},
    'inputgroup': {'model': GroupInputModel, 'form': GroupInputForm, 'pretty': 'Input group', 'hidden': False},
    'outputgroup': {'model': GroupOutputModel, 'form': GroupOutputForm, 'pretty': 'Output group', 'hidden': False},
    'conditiongroup': {'model': GroupConditionModel, 'form': GroupConditionForm, 'pretty': 'Condition', 'hidden': False},
    'areagroup': {'model': GroupAreaModel, 'form': GroupAreaForm, 'pretty': 'Area', 'hidden': False},
    # members
    'connectionmember': {'model': MemberConnectionModel, 'form': MemberConnectionForm, 'pretty': 'Connection member', 'hidden': True, 'redirect': 'connectiongroup'},
    'inputmember': {'model': MemberInputModel, 'form': MemberInputForm, 'pretty': 'Input member', 'hidden': True, 'redirect': 'inputgroup'},
    'outputmember': {'model': MemberOutputModel, 'form': MemberOutputForm, 'pretty': 'Output member', 'hidden': True, 'redirect': 'outputgroup'},
    'conditionlinkmember': {'model': MemberConditionLinkModel, 'form': MemberConditionLinkForm, 'pretty': 'Condition Link Member', 'hidden': True, 'redirect': 'conditionlinkobject'},
    'conditionmember': {'model': MemberConditionModel, 'form': MemberConditionForm, 'pretty': 'Condition Member', 'hidden': True, 'redirect': 'conditiongroup'},
    'conditionoutputmember': {'model': MemberConditionOutputModel, 'form': MemberConditionOutputForm, 'pretty': 'Condition Output Member', 'hidden': True, 'redirect': 'conditiongroup'},
    'conditionoutputgroupmember': {'model': MemberConditionOutputGroupModel, 'form': MemberConditionOutputGroupForm, 'pretty': 'Condition Output Member Group', 'hidden': True,
                                   'redirect': 'conditiongroup'},
    'areamember': {'model': MemberAreaModel, 'form': MemberAreaForm, 'pretty': 'Area Member', 'hidden': True, 'redirect': 'areagroup'},
    'areanestedgroup': {'model': NestedAreaModel, 'form': NestedAreaForm, 'pretty': 'Nested area group', 'hidden': True, 'redirect': 'areagroup'},
}

sub_type_dict = {
    'connectionmember': {
        'object': {
            'model': MemberConnectionModel, 'form': MemberConnectionForm,
            'pretty': 'Device', 'member_key': 'obj', 'group_key': 'group', 'create_redirect': 'connectionobject'
        },
    },
    'inputmember': {
        'object': {
            'model': MemberInputModel, 'form': MemberInputForm,
            'pretty': 'Device', 'member_key': 'obj', 'group_key': 'group', 'create_redirect': 'inputobject'
        },
    },
    'outputmember': {
        'object': {
            'model': MemberOutputModel, 'form': MemberOutputForm,
            'pretty': 'Device', 'member_key': 'obj', 'group_key': 'group', 'create_redirect': 'outputobject'
        },
    },
    'conditionmember': {
        'condition_member_link': {'model': MemberConditionModel, 'form': MemberConditionForm,
                                  'pretty': 'Condition link', 'member_key': 'link', 'group_key': 'group', 'create_redirect': 'conditionlinkobject'},
        'condition_member_output': {'model': MemberConditionOutputModel, 'form': MemberConditionOutputForm,
                                    'pretty': 'Output object', 'member_key': 'obj', 'group_key': 'condition_group', 'create_redirect': 'outputobject'},
        'condition_member_output_group': {'model': MemberConditionOutputGroupModel, 'form': MemberConditionOutputGroupForm,
                                          'pretty': 'Output group', 'member_key': 'group', 'group_key': 'condition_group', 'create_redirect': 'outputgroup'},
        'condition_member_area_group': {'model': MemberConditionAreaGroupModel, 'form': MemberConditionAreaGroupForm,
                                        'pretty': 'Area', 'member_key': 'group', 'group_key': 'condition_group', 'create_redirect': 'areagroup'},
    },
    'conditionlinkmember': {
        'condition_link_member': {'model': MemberConditionLinkModel, 'form': MemberConditionLinkForm, 'member_action': 'conditionobject',
                                  'pretty': 'Condition match', 'member_key': 'condition', 'group_key': 'link', 'create_redirect': 'conditionobject'},
        'condition_link_group': {'model': MemberConditionLinkModel, 'form': MemberConditionLinkForm, 'member_action': 'conditiongroup',
                                 'pretty': 'Nested condition', 'member_key': 'group', 'group_key': 'link', 'create_redirect': 'conditiongroup'}
    },
    'areamember': {
        'connection_object': {'model': MemberAreaModel, 'form': MemberAreaForm,
                              'pretty': 'Connection device', 'member_key': 'connection_obj', 'group_key': 'area', 'create_redirect': 'connectionobject'},
        'connection_group': {'model': MemberAreaModel, 'form': MemberAreaForm,
                             'pretty': 'Connection group', 'member_key': 'connection_group', 'group_key': 'area', 'create_redirect': 'connectiongroup'},
        'input_object': {'model': MemberAreaModel, 'form': MemberAreaForm,
                         'pretty': 'Input device', 'member_key': 'input_obj', 'group_key': 'area', 'create_redirect': 'inputobject'},
        'input_group': {'model': MemberAreaModel, 'form': MemberAreaForm,
                        'pretty': 'Input group', 'member_key': 'input_group', 'group_key': 'area', 'create_redirect': 'inputgroup'},
        'output_object': {'model': MemberAreaModel, 'form': MemberAreaForm,
                          'pretty': 'Output device', 'member_key': 'output_obj', 'group_key': 'area', 'create_redirect': 'outputobject'},
        'output_group': {'model': MemberAreaModel, 'form': MemberAreaForm,
                         'pretty': 'Output group', 'member_key': 'output_group', 'group_key': 'area', 'create_redirect': 'outputgroup'},
        'nested_area': {'model': NestedAreaModel, 'form': NestedAreaForm,
                        'pretty': 'Nested area group', 'member_key': 'nested_group', 'group_key': 'group', 'create_redirect': 'areagroup'},
    },
}
