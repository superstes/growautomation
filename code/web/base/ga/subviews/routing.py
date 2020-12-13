from django.shortcuts import Http404

from ..util import get_route, redirect_if_overwritten, redirect_if_hidden
from ..config.routing import choose_dict, choose_sub_dict
from ..config.site import type_dict, sub_type_dict
from .handlers import handler404


def ChooseView(request, typ, action, uid=None):
    if typ in type_dict:
        if type_dict[typ]['hidden'] is True and action == 'list':
            return redirect_if_hidden(request=request, target=type_dict[typ]['redirect'])

        current_form = type_dict[typ]['form']
        current_model = type_dict[typ]['model']
    else:
        return handler404(request=request, msg=f"Data type '{ typ }' was not found")

    if action not in choose_dict:
        return handler404(request=request, msg=f"Action '{ action }' was not found")

    if typ in sub_type_dict and request.method == 'GET':
        return ChooseSubView(request=request, typ=typ, sub_type=request.GET['typ'], action=action, uid=uid)

    else:
        route = get_route(choose_from=choose_dict, action=action, typ=typ)

        if route is None:
            return choose_dict[action]['*'](request=request, model_obj=current_model, form_obj=current_form, typ=typ, uid=uid)

        else:
            return route(request=request, model_obj=current_model, form_obj=current_form, typ=typ, uid=uid)


def ChooseSubView(request, typ, sub_type, action, uid=None):
    try:
        current_type_dict = sub_type_dict[typ][sub_type]

    except KeyError:
        current_type_dict = None

    if current_type_dict is None:
        raise Http404(f"Data sub-type '{sub_type}' was not found")

    else:
        overwritten = redirect_if_overwritten(request=request, type_dict=current_type_dict)

        if overwritten is not None:
            return overwritten

        current_form = current_type_dict['form']
        current_model = current_type_dict['model']

    if action not in choose_sub_dict:
        raise Http404(f"Action '{action}' was not found")

    route = get_route(choose_from=choose_sub_dict, action=action, typ=typ)

    if route is None:
        return choose_sub_dict[action]['*'](request=request, model_obj=current_model, form_obj=current_form, typ=typ, uid=uid)

    else:
        return route(request=request, model_obj=current_model, form_obj=current_form, typ=typ, uid=uid)
