from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

from ..user import authorized_to_read
from ..config.nav import nav_dict


@user_passes_test(authorized_to_read, login_url='/denied/')
def ListAreaView(request, model_obj, typ):
    member_data_dict = {
        # 'object': objectmember_type_dict['object']['model'].objects.all(),
        # 'group': objectmember_type_dict['group']['model'].objects.all()
    }
    group_show_list = ['area']
    group_key = 'group'

    dataset = model_obj.objects.all()

    return render(request, 'crud/list/member.html', context={
        'dataset': dataset, 'typ': typ, 'request': request, 'member_data_dict': member_data_dict, 'member_type_dict': objectmember_type_dict,
        'group_show_list': group_show_list, 'group_key': group_key, 'nav_dict': nav_dict,
    })
