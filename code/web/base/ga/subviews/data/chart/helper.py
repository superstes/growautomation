from django.shortcuts import redirect

from ....utils.main import get_as_string


def add_ds_chart_options(request, defaults: dict, redirect_path: str):
    out_dict = {}

    for key, value in request.GET.items():
        out_dict[key] = value

    for key, value in defaults.items():
        if key not in request.GET or request.GET[key] is None:
            out_dict[key] = value

    return redirect("%s/%s" % (redirect_path, get_as_string(out_dict)))


def get_param_if_ok(parameters, search: str, choices: list = None, no_choices: list = None, format_as=str):
    if search in parameters:
        if choices is not None:
            if parameters[search] in choices:
                return format_as(parameters[search])

        elif no_choices is not None:
            if parameters[search] not in no_choices:
                return format_as(parameters[search])

        else:
            return format_as(parameters[search])

    return None
