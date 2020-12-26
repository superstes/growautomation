from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

from ...user import authorized_to_read
from ...config.site import sub_type_dict
from ...utils.main import member_pre_process
from ...config.nav import nav_dict


@user_passes_test(authorized_to_read, login_url='/denied/')
def ListConditionView(request, model_obj, typ, form_obj=None, uid=None):
    member_type = 'conditionmember'
    cm_type_dict = sub_type_dict[member_type]
    member_data_dict = {
        'condition_member_link': cm_type_dict['condition_member_link']['model'].objects.all(),
        'condition_member_output': cm_type_dict['condition_member_output']['model'].objects.all(),
        'condition_member_output_group': cm_type_dict['condition_member_output_group']['model'].objects.all(),
    }

    member_view_active, member_data_dict = member_pre_process(member_data_dict=member_data_dict, request=request, type_dict=cm_type_dict)

    group_key = 'group'

    dataset = model_obj.objects.all()

    return render(request, 'crud/list/member.html', context={
        'dataset': dataset, 'typ': typ, 'request': request, 'member_data_dict': member_data_dict, 'member_type_dict': cm_type_dict,
        'group_key': group_key, 'member_type': member_type, 'member_view_active': member_view_active, 'nav_dict': nav_dict,
    })


@user_passes_test(authorized_to_read, login_url='/denied/')
def ListConditionLinkView(request, model_obj, typ, form_obj=None, uid=None):
    member_type = 'conditionlinkmember'
    clm_type_dict = sub_type_dict[member_type]
    member_data_dict = {
        'condition_link_member': clm_type_dict['condition_link_member']['model'].objects.all(),
        'condition_link_group': clm_type_dict['condition_link_group']['model'].objects.all(),
    }

    member_view_active, member_data_dict = member_pre_process(member_data_dict=member_data_dict, request=request, type_dict=clm_type_dict)

    group_key = 'link'

    dataset = model_obj.objects.all()

    return render(request, 'crud/list/member.html', context={
        'dataset': dataset, 'typ': typ, 'request': request, 'member_data_dict': member_data_dict, 'member_type_dict': clm_type_dict,
        'group_key': group_key, 'member_type': member_type, 'member_view_active': member_view_active, 'nav_dict': nav_dict,
    })


