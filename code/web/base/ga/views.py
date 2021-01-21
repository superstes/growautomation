from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from .config.site import type_dict
from .user import authorized_to_access
from .subviews.config.routing import ChooseView, ChooseSubView
from .config.nav import nav_dict
from .utils.main import logout_check
from .subviews.handlers import handler403, handler404, handler403_api, handler404_api
from .subviews.system.logs import LogView
from .subviews.system.service import ServiceView
from .subviews.system.scripts import ScriptView, ScriptChangeView, ScriptDeleteView, ScriptShow
from .subviews.data.raw.input import DataListView
from .subviews.data.chart.main import DataChartView
from .subviews.data.chart.dashboard import DataChartDashboardView, DataChartDatasetLinkView
from .subviews.data.chart.dataset import DataChartDatasetView
from .subviews.data.chart.graph import DataChartGraphView
from .subviews.api.data.main import ApiData
from .subviews.api.chart.main import ApiChart
from .subviews.data.dashboard.main import DashboardView


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
def view_system(request, typ: str, sub_type=None):
    if typ == 'log':
        return logout_check(request=request, default=LogView(request=request))

    elif typ == 'service':
        return logout_check(request=request, default=ServiceView(request=request))

    elif typ == 'script':
        if sub_type is not None:
            if sub_type == 'change':
                return logout_check(request=request, default=ScriptChangeView(request=request))
            elif sub_type == 'delete':
                return logout_check(request=request, default=ScriptDeleteView(request=request))
            elif sub_type == 'show':
                return logout_check(request=request, default=ScriptShow(request=request))

        return logout_check(request=request, default=ScriptView(request=request))

    return logout_check(request=request, default=handler404(request=request, msg='Not yet implemented!'))


@login_required
@user_passes_test(authorized_to_access, login_url=login_url)
def view_data(request, typ: str, sub_type: str = None, third_type: str = None):
    if typ == 'table':
        return logout_check(request=request, default=DataListView(request=request))

    elif typ == 'chart':
        if sub_type == 'dataset':
            return logout_check(request=request, default=DataChartDatasetView(request=request))

        elif sub_type == 'graph':
            return logout_check(request=request, default=DataChartGraphView(request=request))

        elif sub_type == 'dashboard':
            if third_type == 'dataset':
                return logout_check(request=request, default=DataChartDatasetLinkView(request=request))

            return logout_check(request=request, default=DataChartDashboardView(request=request))

        return logout_check(request=request, default=DataChartView(request=request))

    elif typ == 'dashboard':
        return logout_check(request=request, default=DashboardView(request=request))

    return logout_check(request=request, default=handler404(request=request, msg='Not yet implemented!'))


def view_denied(request):
    return logout_check(request=request, default=handler403(request))


@login_required
def view_logout(request):
    return logout_check(request=request, default=handler403(request), hard_logout=True)


# @user_passes_test(authorized_to_access, login_url='/api/denied/', redirect_field_name=None)
def view_api(request, typ: str, sub_type: str = None):
    # no logout check needed since there is no logout button at this route
    if typ == 'data':
        return ApiData(request=request)

    elif typ == 'chart':
        return ApiChart(request=request)

    return handler404_api()


def view_api_denied(request):
    return handler403_api()
