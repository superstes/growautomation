from django import template
from netaddr import IPAddress
from datetime import datetime

from ..config.site import GA_USER_GROUP, GA_READ_GROUP, GA_WRITE_GROUP
from ..utils.helper import get_controller_setting, get_client_ip
from ..config.shared import DATETIME_TS_FORMAT

register = template.Library()


@register.filter
def get_type(value):
    typ = type(value)
    output = str(typ).replace("<class '", '').replace("'>", '')
    return output


@register.filter
def get_item(dictionary, key):
    try:
        if key in dictionary:
            return dictionary.get(key)
        else:
            return None

    except TypeError:  # if object not iterable
        value = getattr(dictionary, key)

        if value:
            return value
        else:
            return None


@register.filter
def get_first_key(dictionary):
    return list(dictionary.keys())[0]


@register.filter
def get_str(obj):
    return str(obj)


@register.simple_tag
def set_var(val):
    return val


@register.filter
def get_dict(var):
    return var.__dict__


@register.filter
def get_keys(obj):
    try:
        return obj.keys()
    except AttributeError:
        return None


@register.filter
def has_key(obj, key):
    try:
        if key in obj:
            return True

        return False
    except TypeError:  # if object not iterable
        if hasattr(obj, key):
            return True
        else:
            return False


@register.filter
def get_login_state(request):
    try:
        state = request.user.is_authenticated
    except AttributeError:
        state = False
    return state


@register.filter
def authorized_to_access(user):
    if user and user.groups.filter(name=GA_USER_GROUP).exists():
        return True

    return False


@register.filter
def authorized_to_read(user):
    if user and user.groups.filter(name=GA_READ_GROUP).exists():
        return True

    return False


@register.filter
def authorized_to_write(user):
    if user and user.groups.filter(name=GA_WRITE_GROUP).exists():
        return True

    return False


@register.filter
def first_upper(string: str):
    if type(string) == str:
        return string.capitalize()

    return string


@register.filter
def count_up(number: int):
    number += 1
    return number


@register.filter
def host_remove_port(http_host: str):
    http_host_wo_port = http_host.split(':')[0]
    return http_host_wo_port


@register.filter
def get_dict_depth(test: dict):
    if isinstance(test, dict):
        soft_depth = max(map(get_dict_depth, test.values()))
        soft_depth += 1
        return soft_depth

    return 0


@register.filter
def get_full_uri(request):
    full_uri = request.build_absolute_uri()
    return full_uri


@register.filter
def to_uppercase(data: str) -> str:
    if type(data) != str:
        return data
    else:
        return data.upper()


@register.filter
def get_return_path(request, typ=None) -> str:
    if 'return' in request.GET:
        path = request.GET['return']

    elif 'return' in request.POST:
        path = request.POST['return']


    else:
        if typ is None:
            path = request.META.get('HTTP_REFERER')

        else:
            path = f"/config/list/{ typ }/"

    if path is None:
        path = '/'

    return path


@register.filter
def handler500_update(request):
    if request.META.get('HTTP_REFERER').find('/update') != -1:
        return True

    return False


@register.filter
def use_cdn(request):
    return get_controller_setting(request, setting='web_cdn')


@register.filter
def hide_warning(request):
    return get_controller_setting(request, setting='web_warn')


@register.filter
def client_is_public(request):
    client_ip = get_client_ip(request)
    ip_is_public = not IPAddress(client_ip).is_reserved()
    return ip_is_public


@register.filter
def format_ts(datetime_obj):
    return datetime.strftime(datetime_obj, DATETIME_TS_FORMAT)


@register.filter
def remove_newline(text: str) -> str:
    return text.replace('\n', '')
