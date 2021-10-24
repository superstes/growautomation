from traceback import format_exc

from django.shortcuts import render
from django.http import JsonResponse

from ..config.shared import LOG_MAX_TRACEBACK_LENGTH
from ..utils.helper import get_server_config, develop_log


class PseudoException(Exception):
    def __init__(self, ga: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ga = ga


class Pseudo404(PseudoException):
    pass


class Pseudo403(PseudoException):
    pass


class Pseudo500(PseudoException):
    pass


def handler400_api(msg=None):
    if msg is None:
        msg = 'api not found'

    return JsonResponse(data={'message': msg}, status=400)


def handler403(exc):
    request = exc.ga['request']
    develop_log(request=request, output=f"{request.build_absolute_uri()} - Got error 403 - {exc.ga['msg']}")
    return render(request, 'error/403.html', context={'request': request, 'error_msg': exc.ga['msg']})


def handler403_api(msg=None):
    if msg is None:
        msg = 'api access denied'

    return JsonResponse(data={'message': msg}, status=403)


def handler404(exc):
    request = exc.ga['request']
    develop_log(request=request, output=f"{request.build_absolute_uri()} - Got error 404 - {exc.ga['msg']}")
    return render(request, 'error/404.html', context={'request': request, 'error_msg': exc.ga['msg']})


def handler404_api(msg=None):
    if msg is None:
        msg = 'api not found'

    return JsonResponse(data={'message': msg}, status=404)


def handler500(exc):
    request = exc.ga['request']
    msg = exc.ga['msg']
    develop_log(request=request, output=f"{request.build_absolute_uri()} - Got error 500 - {msg}")

    if get_server_config(setting='security') == 0:
        develop_log(request=request, output=f"{format_exc(limit=LOG_MAX_TRACEBACK_LENGTH)}", level=2)

    return render(request, '500.html', context={'request': request, 'error_msg': msg})


def handler500_api(msg=None):
    if msg is None:
        msg = 'api error'

    return JsonResponse(data={'message': msg}, status=500)
