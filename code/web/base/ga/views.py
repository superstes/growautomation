from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from .config.site import type_dict
from .user import authorized_to_access
from .subviews.config.routing import ChooseView, ChooseSubView
from .config.nav import nav_dict
from .utils.main import logout_check
from .subviews.handlers import handler403, handler404
from .subviews.system.logs import LogView
from .subviews.system.service import ServiceView


login_url = '/accounts/login/'


@login_required
@user_passes_test(authorized_to_access, login_url=login_url)
def view_config(request, **kwargs):
    view = None

    if 'action' in kwargs and 'typ' in kwargs:
        action = kwargs['action']
        typ = kwargs['typ']
        if 'uid' in kwargs:
            uid = kwargs['uid']
        else:
            uid = None

        if 'sub_type' in kwargs:
            sub_type = kwargs['sub_type']
            view = ChooseSubView(request=request, action=action, typ=typ, sub_type=sub_type, uid=uid)

        else:
            view = ChooseView(request=request, action=action, typ=typ, uid=uid)

    if view is None:
        view = handler404(request)

    return logout_check(request=request, default=view)


@login_required
@user_passes_test(authorized_to_access, login_url=login_url)
def view_home(request):
    return logout_check(request=request, default=render(request, 'home.html', {'type_dict': type_dict, 'nav_dict': nav_dict}))


@login_required
@user_passes_test(authorized_to_access, login_url=login_url)
def view_system(request, typ: str):
    if typ == 'log':
        return logout_check(request=request, default=LogView(request=request))

    elif typ == 'service':
        return logout_check(request=request, default=ServiceView(request=request))

    return logout_check(request=request, default=handler404(request=request, msg='Not yet implemented!'))
    # return logout_check(request=request, default=render(request, 'system/main.html', {'type_dict': type_dict, 'nav_dict': nav_dict}))


@login_required
@user_passes_test(authorized_to_access, login_url=login_url)
def view_data(request, typ: str):
    return logout_check(request=request, default=handler404(request=request, msg='Not yet implemented!'))
    # return logout_check(request=request, default=render(request, 'data/main.html', {'type_dict': type_dict, 'nav_dict': nav_dict}))


@login_required
def view_denied(request):
    return logout_check(request=request, default=handler403(request))


@login_required
def view_logout(request):
    return logout_check(request=request, default=handler403(request), hard_logout=True)
