from traceback import format_exc

from django.shortcuts import render
from django.http import JsonResponse

from core.utils.debug import web_log

from ..config.shared import LOG_MAX_TRACEBACK_LENGTH
from ..utils.helper import get_server_config


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


def input_check(exc) -> dict:
    output = {}

    if isinstance(exc, Exception):
        output['request'] = None
        output['msg'] = str(exc)

    elif hasattr(exc, 'ga'):
        output['request'] = exc.ga['request']
        output['msg'] = exc.ga['msg']

    elif type(exc) == dict and 'ga' in exc:
        output['request'] = exc['ga']['request']
        output['msg'] = exc['ga']['msg']

    else:
        output['request'] = exc
        output['msg'] = 'Got no error message.'

    return output


def handler_log(output: dict, status: int):
    if output['request'] is None:
        web_log(output=f"Got error {status} - {output['msg']}")

    else:
        web_log(output=f"{output['request'].build_absolute_uri()} - Got error {status} - {output['msg']}")


def handler400_api(msg=None):
    if msg is None:
        msg = 'api not found'

    return JsonResponse(data={'message': msg}, status=400)


def handler403(exc):
    output = input_check(exc)
    handler_log(output=output, status=403)
    return render(output['request'], 'error/403.html', context={'request': output['request'], 'error_msg': output['msg']})


def handler403_api(msg=None):
    if msg is None:
        msg = 'api access denied'

    return JsonResponse(data={'message': msg}, status=403)


def handler404(exc):
    output = input_check(exc)
    handler_log(output=output, status=404)
    return render(output['request'], 'error/404.html', context={'request': output['request'], 'error_msg': output['msg']})


def handler404_base(request, exception):
    return handler404({'ga': {'request': request, 'msg': str(exception)}})


def handler404_api(msg=None):
    if msg is None:
        msg = 'api not found'

    return JsonResponse(data={'message': msg}, status=404)


def handler500(exc):
    output = input_check(exc)
    handler_log(output=output, status=500)

    if get_server_config(setting='security') == 0:
        web_log(output=f"{format_exc(limit=LOG_MAX_TRACEBACK_LENGTH)}", level=2)

    return render(output['request'], '500.html', context={'request': output['request'], 'error_msg': output['msg']})


def handler500_api(msg=None):
    if msg is None:
        msg = 'api error'

    return JsonResponse(data={'message': msg}, status=500)
