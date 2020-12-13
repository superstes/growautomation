from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import user_passes_test

from .config.site import type_dict
from .user import authorized_to_access
from .subviews.routing import ChooseView, ChooseSubView
from .config.nav import nav_dict
from .util import get_url_attribute
from .subviews.handlers import handler500, handler403


def LoginCheck(request):
    if request.user.is_authenticated:
        return Precheck(request)
    else:
        return LoginView.as_view()(request)


@login_required
@user_passes_test(authorized_to_access, login_url='/accounts/login/')
def Precheck(request):
    # handling of global states
    if request.method == 'POST':
        if 'logout' in request.POST and int(request.POST['logout']) == 1:
            return logout_then_login(request)

    # processing for paths
    path_list = request.META['PATH_INFO'].split('/')[1:]

    print("Precheck | POST: %s, GET: %s, USER: %s, path_list: %s" % (request.POST, request.GET, request.user, path_list))
    route = get_url_attribute(url_list=path_list, target_index=0)
    action = get_url_attribute(url_list=path_list, target_index=1)

    if route == 'config':
        typ = get_url_attribute(url_list=path_list, target_index=2, target_type=str)
        uid = get_url_attribute(url_list=path_list, target_index=3, target_type=int)
        if type(uid) == str:
            sub_type = get_url_attribute(url_list=path_list, target_index=3, target_type=str)
            uid = get_url_attribute(url_list=path_list, target_index=4, target_type=int)
        else:
            sub_type = None

    return_value = None

    if route:
        if route == 'config':
            if sub_type and type(sub_type) == str and typ and action:
                return_value = ChooseSubView(request=request, action=action, typ=typ, sub_type=sub_type, uid=uid)

            elif typ and action:
                return_value = ChooseView(request=request, action=action, typ=typ, uid=uid)

        # elif route == 'data':
        #     return handler404(request)
        #
        # elif route == 'system':
        #     return handler404(request)

        elif route in ['home', 'main', '']:
            return_value = render(request, 'home.html', {'type_dict': type_dict, 'nav_dict': nav_dict})

        elif route in ['denied', 'list', 'detailed', 'create', 'update', 'delete']:
            return_value = handler403(request)

    elif route is None:
        return_value = render(request, 'home.html', {'type_dict': type_dict, 'nav_dict': nav_dict})

    if return_value is None:
        return handler500(request, msg='Server found nothing to load.')

    else:
        return return_value
