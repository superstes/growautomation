from django.shortcuts import redirect

from ...utils.main import get_as_string
from ...utils.helper import get_form_prefill, empty_key, get_url_divider, set_key


def get_existing_params_dict(source: dict) -> dict:
    existing_params = {}

    for param, value in source.items():
        existing_params[param] = value

    return existing_params


def add_default_chart_options(request, defaults: dict, redirect_path: str) -> (None, redirect):
    missing_params = {}

    for key, value in defaults.items():
        if empty_key(request.GET, param=key) and set_key(defaults, param=key):
            missing_params[key] = value

    if len(missing_params) == 0:
        return None

    divider = get_url_divider(redirect_path)

    return redirect("%s%s%s" % (redirect_path, divider, get_as_string({**get_existing_params_dict(request.GET), **missing_params})))


def get_param_if_ok(parameters, search: str, choices: list = None, no_choices: list = None, format_as: (str, int, list, dict, bool) = str, fallback=None,
                    lower: bool = False):
    try:
        if search in parameters:
            if choices is not None:
                if format_as == str and lower:
                    if parameters[search].lower() in choices:
                        return format_as(parameters[search]).lower()
                else:
                    if parameters[search] in choices:
                        return format_as(parameters[search])

            elif no_choices is not None:
                if format_as == str and lower:
                    if parameters[search].lower() not in no_choices:
                        return format_as(parameters[search]).lower()

                else:
                    if parameters[search] not in no_choices:
                        return format_as(parameters[search])

            else:
                if format_as == str and lower:
                    return format_as(parameters[search]).lower()

                else:
                    return format_as(parameters[search])

        return fallback

    except ValueError:
        return fallback


def get_obj_dict(request, typ_model, typ_form, selected: str = None, selected_id: int = None) -> dict:
    if request.method == 'GET':
        data = request.GET
    else:
        data = request.POST

    if selected_id is not None:
        _id = selected_id

    else:
        _id = get_param_if_ok(data, search=selected, no_choices=['---------'], format_as=int)

    obj_list = typ_model.objects.all()

    try:
        _obj = [obj for obj in obj_list if obj.id == int(_id)][0]
        form = typ_form(instance=_obj)

    except (IndexError, TypeError):
        _obj = None
        form = typ_form(data, initial=get_form_prefill(request))

    return {'id': _id, 'obj': _obj, 'form': form, 'list': obj_list}


def add_graph_params_to_url(request, chart_dict: dict, redirect_path: str) -> (None, redirect):
    # add graph get params if graph was selected
    if set_key(chart_dict, param='id') and set_key(chart_dict, param='obj'):
        missing_params = {}
        existing_params = {key: value for key, value in request.GET.items()}

        for field in chart_dict['obj'].field_list:
            data = getattr(chart_dict['obj'], field)

            if field not in existing_params:
                if field == 'input_device':
                    data = chart_dict['obj'].input_device.id

                missing_params[field] = data

            # created endless loop; must be debugged if needed
            # else:
            #     if str(existing_params[field]) != str(data):
            #         existing_params.pop(field)
            #         missing_params[field] = data

        if len(missing_params) == 0:
            return None

        divider = get_url_divider(redirect_path)
        return redirect("%s%s%s" % (redirect_path, divider, get_as_string({**missing_params, **get_existing_params_dict(existing_params)})))

    return None
