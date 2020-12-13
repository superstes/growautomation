from django.shortcuts import render
from ..config.nav import nav_dict


def handler403(request, msg=None):
    return render(request, 'error/403.html', context={'request': request, 'nav_dict': nav_dict, 'error_msg': msg})


def handler404(request, msg=None):
    return render(request, 'error/404.html', context={'request': request, 'nav_dict': nav_dict, 'error_msg': msg})


def handler500(request, msg=None):
    return render(request, 'error/500.html', context={'request': request, 'nav_dict': nav_dict, 'error_msg': msg})
