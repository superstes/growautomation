from urllib import parse
from random import choice as random_choice
from string import ascii_letters, digits, punctuation

from django.contrib.auth.views import LoginView, logout_then_login
from django.shortcuts import redirect


def get_as_string(get_params):
    return "?%s" % parse.urlencode(get_params)


def get_route(choose_from, action, typ):
    route = None

    for choose_type, choose_route in choose_from[action].items():
        if choose_type == '*':
            continue

        elif choose_type == '*list':
            for list_dict in choose_route.values():
                if typ in list_dict['option']:
                    route = list_dict['value']
                    break

        else:
            if choose_type == typ:
                route = choose_route
                break

    return route


def redirect_if_overwritten(request, type_dict: dict):
    if 'action' in request.GET:
        overwrite_action = request.GET['action'].lower()
        if overwrite_action == 'create':
            try:
                redirect_url = "/config/create/%s/%s" % (type_dict['create_redirect'], get_as_string(request.GET))
                return redirect(redirect_url)

            except KeyError:
                return None

        elif overwrite_action == 'list':
            try:
                redirect_url = "/config/list/%s/%s" % (type_dict['create_redirect'], get_as_string(request.GET))
                return redirect(redirect_url)

            except KeyError:
                return None

    return None


def redirect_if_hidden(request, target: str):
    redirect_url = f"/config/list/{ target }/{ get_as_string(request.GET) }"

    return redirect(redirect_url)


def member_pre_process(request, member_data_dict: dict, type_dict: dict):
    output = {}
    member_view_active = False

    if 'list_member' in request.GET:
        member_view_active = request.GET['list_member']

        for key, data in member_data_dict.items():
            group_key = type_dict[key]['group_key']
            member_key = type_dict[key]['member_key']

            for member in data:
                member_group = getattr(member, group_key)
                member_repr = getattr(member, member_key)
                if member_group.name == member_view_active and member_repr is not None:
                    if key in output:
                        _member_list = output[key]
                        _member_list.append(member)
                        output[key] = _member_list
                    else:
                        output[key] = [member]

    if member_view_active is False:
        return member_view_active, member_data_dict
    else:
        return member_view_active, output


def _try_type(typ, data: str):
    try:
        _ = typ(data)
        return _

    except ValueError:
        return None


def _get_attribute_type(data: str, typ):
    if typ is not None:
        try_list = [typ]
    else:
        try_list = [int, dict, str]

    for typ in try_list:
        _ = _try_type(typ, data)
        if _ is not None:
            return _


def get_url_attribute(url_list: list, target_index: int, target_type=None):
    try:
        _ = url_list[target_index]

        if _ == '':
            return None

        return _get_attribute_type(data=_, typ=target_type)

    except IndexError:
        return None


def get_random_string(length):
    letters = ascii_letters + digits + punctuation
    return ''.join(random_choice(letters) for _ in range(length))


def find_one_of_list(string: str, search_list: list) -> tuple:
    result, found = False, None

    for search_string in search_list:
        if string.find(search_string) != -1:
            result = True
            found = search_string

    return result, found


def login_check(request, default):
    if request.user.is_authenticated:
        return default
    else:
        return LoginView.as_view()(request)


def logout_check(request, default):
    if request.method == 'POST':
        if 'logout' in request.POST and int(request.POST['logout']) == 1:
            return logout_then_login(request)

    return default
