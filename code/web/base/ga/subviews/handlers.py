from django.shortcuts import render
from django.http import JsonResponse


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


def handler403(request, msg=None):
    return render(request, 'error/403.html', context={'request': request, 'error_msg': msg})


def handler403_api(msg=None):
    if msg is None:
        msg = 'api access denied'

    return JsonResponse(data={'message': msg}, status=403)


def handler404(request, msg=None):
    return render(request, 'error/404.html', context={'request': request, 'error_msg': msg})


def handler404_api(msg=None):
    if msg is None:
        msg = 'api not found'

    return JsonResponse(data={'message': msg}, status=404)


def handler500(request, msg=None):
    if request is None:
        return render(request, 'error/500_basic.html', context={'error_msg': msg})

    return render(request, 'error/500.html', context={'request': request, 'error_msg': msg})


def handler500_api(msg=None):
    if msg is None:
        msg = 'api error'

    return JsonResponse(data={'message': msg}, status=500)
