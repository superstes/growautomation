from sys import platform
from datetime import datetime
from pytz import timezone as pytz_timezone
from django.utils import timezone as django_timezone

from core.utils.process import subprocess

from ..models import ObjectControllerModel
from ..models import ObjectInputModel, ObjectOutputModel, ObjectConnectionModel
from ..models import MemberInputModel, MemberOutputModel, MemberConnectionModel
from ..subviews.handlers import handler404
from ..config.shared import DATETIME_TS_FORMAT


DEVICE_TYPES = [ObjectInputModel, ObjectOutputModel, ObjectConnectionModel]


def check_develop(request) -> bool:
    server = request.META.get('wsgi.file_wrapper', None)
    if server is not None and server.__module__ in ['django.core.servers.basehttp', 'wsgiref.util']:
        return True

    return False


def get_time_difference(time_data: str, time_format: str) -> int:
    before = datetime.strptime(time_data, time_format)
    now = datetime.now()
    difference = now - before

    return int(difference.total_seconds())


def get_controller_obj():
    return [cont for cont in ObjectControllerModel.objects.all()][0]


def get_controller_setting(request, setting: str):
    try:
        return getattr(get_controller_obj(), setting)

    except IndexError:
        raise handler404(request, msg="Can't get controller setting if no controller exists. You must create a controller first.")


def get_script_dir(request, typ) -> str:
    path_root = get_controller_setting(request, setting='path_root')

    if platform == 'win32':
        output = "C:/Users/rene/Documents/code/ga/growautomation/code/device/%s" % typ.lower()
    else:
        output = "%s/device/%s" % (path_root, typ.lower())

    return output


def get_client_ip(request):
    ip_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_forwarded:
        client_ip = ip_forwarded.split(',')[0]
    else:
        client_ip = request.META.get('REMOTE_ADDR')

    censored_client_ip = "%s.0" % client_ip.rsplit('.', 1)[0]

    return censored_client_ip


def develop_subprocess(request, command: str, develop: str = None) -> str:
    if check_develop(request):
        return develop

    return subprocess(command)


def add_timezone(request, datetime_obj):
    dt_w_tz = django_timezone.make_aware(datetime_obj, timezone=pytz_timezone(get_controller_setting(request, setting='timezone')))
    return dt_w_tz


def get_device_parent(child_obj):
    parent = None
    member_link_list = None

    if isinstance(child_obj, ObjectInputModel):
        member_link_list = MemberInputModel.objects.all()

    elif isinstance(child_obj, ObjectOutputModel):
        member_link_list = MemberOutputModel.objects.all()

    elif isinstance(child_obj, ObjectConnectionModel):
        member_link_list = MemberConnectionModel.objects.all()

    if member_link_list is not None:
        for link in member_link_list:
            if link.obj == child_obj:
                parent = link.group
                break

    return parent


def get_instance_from_id(typ, obj: (str, int), force_id: bool = False):
    if obj in [None, '', 'None']:
        return None

    for check_obj in typ.objects.all():
        if type(obj) == str:
            if force_id:
                if check_obj.id == int(obj):
                    return check_obj

            else:
                if check_obj.name == obj:
                    return check_obj

        else:
            if check_obj.id == obj:
                return check_obj

    return None


def get_instance_from_field(typ, field: str, data, target_type):
    for check_obj in typ.objects.all():
        if not hasattr(check_obj, field):
            return None

        else:
            if getattr(check_obj, field) == target_type(data):
                return check_obj

    return None


def get_device_instance(obj: (str, int)):
    for typ in DEVICE_TYPES:
        result = get_instance_from_id(typ=typ, obj=obj)
        if result is not None:
            return result


def get_device_parent_setting(child_obj, setting: str):
    if type(child_obj) in [str, int]:
        child_obj = get_device_instance(obj=child_obj)

    parent = get_device_parent(child_obj)

    return getattr(parent, setting)


def get_datetime_w_tz(request, dt_str: str) -> (None, datetime):  # str datetime to tz-aware datetime obj
    if type(dt_str) != str:
        return None
    try:
        _ts_wo_tz = datetime.strptime(dt_str, DATETIME_TS_FORMAT)
        ts_w_tz = add_timezone(request, datetime_obj=_ts_wo_tz)
        return ts_w_tz

    except ValueError:
        return None


def get_form_prefill(request):
    form_prefill = {}

    for key, value in request.GET.items():
        if value is not None:
            form_prefill[key] = value

    return form_prefill


def add_line_numbers(data: (list, str), reverse: bool = False) -> str:
    if type(data) == str:
        data = data.split('\n')
        join_str = '\n'

    else:
        join_str = ''

    if reverse:
        data.reverse()

    output = []

    count = 1
    _zfill_count = len(str(len(data)))

    for line in data:
        output.append("%s | %s" % (str(count).zfill(_zfill_count), line))
        count += 1

    return join_str.join(output)


def empty_key(search, param: str) -> bool:
    if param in search and search[param] not in [None, '', "['']", 'None']:
        return False

    return True


def set_key(search, param: str) -> bool:
    return not empty_key(search=search, param=param)


def get_url_divider(url: str):
    if url.endswith('/'):
        return ''
    else:
        return '/'
