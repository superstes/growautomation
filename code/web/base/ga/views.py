from traceback import format_exc

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

from .config.site import type_dict
from .subviews.config.main import ConfigView
from .utils.main import logout_check
from .utils.helper import develop_log, get_controller_setting
from .user import authorized_to_access
from .subviews.handlers import handler403, handler404, handler403_api, handler404_api, handler500
from .subviews.handlers import Pseudo403, Pseudo404, Pseudo500
from .subviews.system.logs import LogView
from .subviews.system.service import ServiceView
from .subviews.system.scripts import ScriptView, ScriptChangeView, ScriptDeleteView, ScriptShow
from .subviews.data.raw.input import DataListView
from .subviews.data.chart.main import DataChartView, DataChartDatasetView, DataChartGraphView, DataChartDbeView, DataChartDbeGraphView, DataChartDbeDatasetView
from .subviews.api.data.main import ApiData
from .subviews.api.chart.main import ApiChart
from .subviews.data.dashboard.main import DashboardView
from .subviews.system.export import export_view


def view(request, **kwargs):
    return GaView().start(request=request, **kwargs)


class GaView:
    MAX_TRACEBACK_LENGTH = 5000

    def start(self, request, a: str = None, b: str = None, c: str = None, d: str = None, e: str = None):
        try:
            if a == 'denied':
                return self.denied(request=request)

            elif a == 'api_denied':
                return self.api_denied(request=request)

            elif a == 'api':
                return self.api(request=request, typ=b)

            if a == 'logout':
                return self.logout(request=request)

            if a == 'config':
                if e is not None:
                    return self.config(request=request, action=b, typ=c, sub_type=d, uid=int(e))
                elif d is not None:
                    try:
                        return self.config(request=request, action=b, typ=c, uid=int(d))
                    except ValueError:
                        return self.config(request=request, action=b, typ=c, sub_type=d)
                return self.config(request=request, action=b, typ=c)

            elif a == 'system':
                if c is not None:
                    return self.system(request=request, typ=b, sub_type=c)
                return self.system(request=request, typ=b)

            elif a == 'data':
                if d is not None:
                    return self.data(request=request, typ=b, sub_type=c, third_type=d)
                elif c is not None:
                    return self.data(request=request, typ=b, sub_type=c)
                return self.data(request=request, typ=b)

            else:
                return self.home(request=request)

        except Pseudo404 as exc:
            develop_log(request=request, output=f"{request.build_absolute_uri()} - Got error 404 - {exc.ga['msg']}")
            return handler404(request=exc.ga['request'], msg=exc.ga['msg'])

        except Pseudo403 as exc:
            develop_log(request=request, output=f"{request.build_absolute_uri()} - Got error 403 - {exc.ga['msg']}")
            return handler403(request=exc.ga['request'], msg=exc.ga['msg'])

        except Pseudo500 as exc:
            trace = format_exc()
            develop_log(request=request, output=f"{request.build_absolute_uri()} - Got error 500 - {exc.ga['msg']}")
            if get_controller_setting(request=request, setting='security') == 0:
                develop_log(request=request, output=f"{trace}"[:self.MAX_TRACEBACK_LENGTH], level=2)
            return handler500(request=exc.ga['request'], msg=exc.ga['msg'], tb=trace)

        except Exception as error:
            trace = format_exc()
            develop_log(request=request, output=f"{request.build_absolute_uri()} - Got error 500 - {error}")
            if get_controller_setting(request=request, setting='security') == 0:
                develop_log(request=request, output=f"{trace}"[:self.MAX_TRACEBACK_LENGTH], level=2)
            return handler500(request=request, msg=error, tb=trace)

    @staticmethod
    @login_required
    @user_passes_test(authorized_to_access, login_url='/accounts/login/')
    def home(request):
        return logout_check(request=request, default=render(request, 'home.html', {'type_dict': type_dict}))

    @staticmethod
    @login_required
    @user_passes_test(authorized_to_access, login_url='/accounts/login/')
    def config(request, action: str, typ: str, uid: int = None, sub_type: str = None):
        return logout_check(request=request, default=ConfigView(request=request, typ=typ, action=action, sub_type=sub_type, uid=uid).go())

    @staticmethod
    @login_required
    @user_passes_test(authorized_to_access, login_url='/accounts/login/')
    def system(request, typ: str, sub_type: str = None):
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

        elif typ == 'export':
            if sub_type is not None:
                return logout_check(request=request, default=export_view(request=request, process=sub_type))

            return logout_check(request=request, default=export_view(request=request, process='config'))

        raise Pseudo404(ga={'request': request, 'msg': 'Not implemented!'})

    @staticmethod
    @login_required
    @user_passes_test(authorized_to_access, login_url='/accounts/login/')
    def data(request, typ: str, sub_type: str = None, third_type: str = None):
        if typ == 'table':
            return logout_check(request=request, default=DataListView(request=request))

        elif typ == 'chart':
            if sub_type == 'dataset':
                return logout_check(request=request, default=DataChartDatasetView(request=request))

            elif sub_type == 'graph':
                return logout_check(request=request, default=DataChartGraphView(request=request))

            elif sub_type == 'dbe':
                if third_type == 'dataset':
                    return logout_check(request=request, default=DataChartDbeDatasetView(request=request))

                elif third_type == 'graph':
                    return logout_check(request=request, default=DataChartDbeGraphView(request=request))

                return logout_check(request=request, default=DataChartDbeView(request=request))

            return logout_check(request=request, default=DataChartView(request=request))

        elif typ == 'dashboard':
            if sub_type == 'config':
                if third_type is not None:
                    return logout_check(request=request, default=DashboardView(request=request).go_config(info=third_type))

                return logout_check(request=request, default=DashboardView(request=request).go_config())

            return logout_check(request=request, default=DashboardView(request=request).go_main())

        raise Pseudo404(ga={'request': request, 'msg': 'Not implemented!'})

    @staticmethod
    def denied(request):
        error_source_url = request.build_absolute_uri(request.META['QUERY_STRING'].split('=', 1)[1])
        develop_log(request=request, output=f"{error_source_url} - Got error 403 - Access denied for user \"{request.user}\"")
        return logout_check(request=request, default=handler403(request))

    @staticmethod
    @login_required
    def logout(request):
        return logout_check(request=request, default=handler403(request), hard_logout=True)

    @staticmethod
    def api(request, typ: str):
        # no logout check needed since there is no logout button at this route
        if typ == 'data':
            return ApiData(request=request).go()

        elif typ == 'chart':
            return ApiChart(request=request)

        develop_log(request=request, output=f"{request.build_absolute_uri()} - Got error 404 - api not implemented")
        return handler404_api()

    @staticmethod
    def api_denied(request):
        error_source_url = request.build_absolute_uri(request.META['QUERY_STRING'].split('=', 1)[1])
        develop_log(request=request, output=f"{error_source_url} - Got error 403 - api access denied")
        return handler403_api()
