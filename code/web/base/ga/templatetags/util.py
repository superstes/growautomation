from django import template
from netaddr import IPAddress
from datetime import datetime, timedelta
from random import randint
from sys import exc_info as sys_exc_info
from os import environ as os_environ

from ..config.shared import GA_WRITE_GROUP, WEBUI_EMPTY_CHOICE
from ..utils.helper import get_controller_setting
from ..utils.web import get_client_ip
from ..config.shared import DATETIME_TS_FORMAT, VERSION
from ..config.nav import NAVIGATION

register = template.Library()


@register.filter
def get_type(value):
    typ = type(value)
    output = str(typ).replace("<class '", '').replace("'>", '')
    return output


@register.filter
def get_item(data, key):
    value = None

    try:
        if key.find(',') != -1:
            # workaround since template does only support two arguments for filters
            key, fallback = key.split(',', 1)

        else:
            fallback = None
    except AttributeError:
        fallback = None

    try:
        if key in data:
            value = data.get(key)
    except TypeError:
        if hasattr(data, key):
            value = getattr(data, key)

    if value is not None:
        return value

    return fallback


@register.simple_tag
def set_var(val):
    return val


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
def authorized_to_write(user):
    if user and user.groups.filter(name=GA_WRITE_GROUP).exists():
        return True

    return False


@register.filter
def get_full_uri(request):
    full_uri = request.build_absolute_uri()
    return full_uri


@register.filter
def get_return_path(request, typ=None) -> str:
    # todo: refactor => Ticket#26
    return '/'
    # path = None
    #
    # if 'return' in request.GET:
    #     path = request.GET['return']
    #
    # elif 'return' in request.POST:
    #     path = request.POST['return']
    #
    # # else:
    # #     if typ is None:
    # #         path = request.META['HTTP_REFERER']
    # #
    # #     else:
    # #         path = f"/config/list/{ typ }/"
    #
    # if path is None:
    #     path = '/'
    #
    # return path


@register.filter
def use_cdn(request):
    return get_controller_setting(request, setting='web_cdn')


@register.filter
def hide_warning(request):
    return get_controller_setting(request, setting='web_warn')


@register.filter
def security_mode(request):
    return get_controller_setting(request, setting='security')


@register.filter
def client_is_public(request):
    client_ip = get_client_ip(request)
    ip_is_public = not IPAddress(client_ip).is_reserved()
    return ip_is_public


@register.filter
def format_ts(datetime_obj):
    return datetime.strftime(datetime_obj, DATETIME_TS_FORMAT)


@register.filter
def format_seconds(secs: int) -> str:
    return "{}".format(str(timedelta(seconds=secs)))


@register.filter
def request_getlist(request, parameter: str) -> list:
    if parameter in request.GET:
        return request.GET.getlist(parameter)

    else:
        return []


@register.simple_tag
def random_gif() -> str:
    return f"img/500/{randint(1, 20)}.gif"


@register.simple_tag
def get_last_errors() -> str:
    error_type = str(sys_exc_info()[0]).split("'", 3)[1]
    error_msg = sys_exc_info()[1]
    return f"{error_type} => {error_msg}"


@register.filter
def get_nav(key: str) -> dict:
    # serves navigation config to template
    return NAVIGATION[key]


@register.filter
def found(data: str, search: str) -> bool:
    if data.find(search) != -1:
        return True

    return False


@register.simple_tag
def demo_mode() -> bool:
    if 'GA_DEMO' in os_environ:
        return True

    return False


@register.simple_tag
def beta_mode() -> bool:
    if 'GA_BETA' in os_environ:
        return True

    return False


@register.simple_tag
def get_version() -> float:
    return VERSION


@register.simple_tag
def get_empty() -> str:
    return WEBUI_EMPTY_CHOICE


@register.filter
def empty_if_none(check: str) -> str:
    if check in [None, 'None']:
        return ''

    return check
