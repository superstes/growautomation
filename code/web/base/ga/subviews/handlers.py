from django.shortcuts import render
from django.http import JsonResponse

from ..config.nav import nav_dict


def handler403(request, msg=None):
    return render(request, 'error/403.html', context={'request': request, 'nav_dict': nav_dict, 'error_msg': msg})


def handler403_api(msg=None):
    if msg is None:
        msg = 'api access denied'

    return JsonResponse(data={'message': msg}, status=403)


def handler404(request, msg=None):
    return render(request, 'error/404.html', context={'request': request, 'nav_dict': nav_dict, 'error_msg': msg})


def handler404_api(msg=None):
    if msg is None:
        msg = 'api not found'

    return JsonResponse(data={'message': msg}, status=404)


def handler500(request, msg=None):
    if request is None:
        return render(request, 'error/500_basic.html', context={'error_msg': msg})

    return render(request, 'error/500.html', context={'request': request, 'nav_dict': nav_dict, 'error_msg': msg})


def handler500_api(msg=None):
    if msg is None:
        msg = 'api error'

    return JsonResponse(data={'message': msg}, status=500)
