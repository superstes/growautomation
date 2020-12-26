from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

from ...user import authorized_to_read
from ...config.site import sub_type_dict
from ...utils.main import member_pre_process
from ...config.nav import nav_dict


@user_passes_test(authorized_to_read, login_url='/denied/')
def ListGroupView(request, model_obj, typ, form_obj=None, uid=None):
    group_type = typ[:-5]  # remove 'group' from grouptype name
    member_type = "%smember" % group_type

    m_type_dict = sub_type_dict[member_type]

    member_data_dict = {
        key: m_type_dict[key]['model'].objects.all() for key in m_type_dict.keys()
    }

    member_view_active, member_data_dict = member_pre_process(member_data_dict=member_data_dict, request=request, type_dict=m_type_dict)

    # group_hide_list = ['condition', 'area']

    dataset = model_obj.objects.all()

    return render(request, 'crud/list/member.html', context={
        'dataset': dataset, 'typ': typ, 'request': request, 'nav_dict': nav_dict, 'member_type': member_type, 'member_view_active': member_view_active,
        'member_data_dict': member_data_dict, 'member_type_dict': m_type_dict,
    })
