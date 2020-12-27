from sys import platform
from datetime import datetime

from ..models import ObjectControllerModel
from ..subviews.handlers import handler404


def check_develop() -> bool:
    if platform == 'win32':
        return True

    else:
        return False


def get_time_difference(time_data: str, time_format: str) -> int:
    before = datetime.strptime(time_data, time_format)
    now = datetime.now()
    difference = now - before

    return int(difference.total_seconds())


def get_controller_setting(request, setting: str):
    try:
        controller = [cont for cont in ObjectControllerModel.objects.all()][0]
        return getattr(controller, setting)

    except IndexError:
        raise handler404(request, msg="Can't get controller setting if no controller exists. You must create a controller first.")


def get_script_dir(request, typ) -> str:
    path_root = get_controller_setting(request, setting='path_root')

    if platform == 'win32':
        output = "C:/Users/rene/Documents/code/ga/growautomation/code/device/%s" % typ.lower()
    else:
        output = "%s/device/%s/" % (path_root, typ.lower())

    return output


def get_client_ip(request):
    ip_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_forwarded:
        client_ip = ip_forwarded.split(',')[0]
    else:
        client_ip = request.META.get('REMOTE_ADDR')

    censored_client_ip = "%s.0" % client_ip.rsplit('.', 1)[0]

    return censored_client_ip
