from django.shortcuts import redirect

from ....utils.main import get_as_string
from ....utils.helper import get_form_prefill


def add_ds_chart_options(request, defaults: dict, redirect_path: str):
    out_dict = {}

    for key, value in request.GET.items():
        out_dict[key] = value

    for key, value in defaults.items():
        if key not in request.GET or request.GET[key] is None:
            out_dict[key] = value

    return redirect("%s/%s" % (redirect_path, get_as_string(out_dict)))


def get_param_if_ok(parameters, search: str, choices: list = None, no_choices: list = None, format_as: (str, int, list, dict, bool) = str, fallback=None):
    if search in parameters:
        if choices is not None:
            if parameters[search] in choices:
                return format_as(parameters[search])

        elif no_choices is not None:
            if parameters[search] not in no_choices:
                return format_as(parameters[search])

        else:
            return format_as(parameters[search])

    return fallback


def get_obj_dict(request, typ_model, typ_form, action: str, selected: str = None, selected_id: int = None) -> dict:
    if selected_id is not None:
        _id = selected_id
    else:
        _id = get_param_if_ok(request.GET, search=selected, no_choices=['---------'], format_as=int)

    _obj = None
    obj_list = typ_model.objects.all()

    if _id and action in ['update', 'show', 'delete']:
        try:
            _obj = [obj for obj in obj_list if obj.id == int(_id)][0]
        except IndexError:
            pass

    if _obj:
        form = typ_form(instance=_obj)
    else:
        form = typ_form(request.GET, initial=get_form_prefill(request))

    return {'id': _id, 'obj': _obj, 'form': form, 'list': obj_list}
