from django.shortcuts import render, Http404, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test

from ...forms import LABEL_DICT, HELP_DICT
from .filter import get_filter_dict, apply_filter
from ...user import authorized_to_read, authorized_to_write
from ...config.nav import nav_dict


@user_passes_test(authorized_to_read, login_url='/denied/')
def ListView(request, model_obj, typ, form_obj=None, uid=None):
    dataset = model_obj.objects.all()

    try:
        filter_dict = get_filter_dict(model_obj.filter_dict, dataset)
        dataset, active_filter = apply_filter(request=request, dataset=dataset)
    except AttributeError as error_msg:
        active_filter = None

        if str(error_msg).find("has no attribute 'filter_dict'") != -1:
            filter_dict = {}
        else:
            filter_dict = error_msg

    return render(request, 'crud/list/default.html', context={
        'dataset': dataset, 'typ': typ, 'filter_dict': filter_dict, 'request': request, 'active_filter': active_filter,  'nav_dict': nav_dict,
    })


@user_passes_test(authorized_to_read, login_url='/denied/')
def DetailView(request, uid, model_obj, typ, form_obj=None):

    try:
        data = model_obj.objects.get(id=uid)
    except model_obj.DoesNotExist:
        raise Http404('Data does not exist')

    data_dict = {}

    for attribute in data.field_list:
        form_widget = form_obj.base_fields[attribute].widget
        if hasattr(form_widget, 'render_value') and form_widget.render_value is False:
            value = '●●●●●●●●●●●●'
        else:
            value = getattr(data, attribute)

        if attribute in LABEL_DICT:
            name = LABEL_DICT[attribute]
        else:
            name = attribute.capitalize()

        if attribute in HELP_DICT:
            info = HELP_DICT[attribute]
        else:
            info = '---'

        data_dict[name] = {'value': value, 'info': info}

    return render(request, 'crud/detailed.html',
                  context={'data': data, 'data_dict': data_dict, 'typ': typ, 'nav_dict': nav_dict})


@user_passes_test(authorized_to_read, login_url='/denied/')
def CreateView(request, form_obj, typ, model_obj=None, uid=None):
    if request.method == 'POST':
        form = form_obj(request.POST)

        if form.is_valid():
            try:
                form.save()
                return redirect("/config/list/%s/" % typ)

            except ValueError as error_msg:
                return render(request, 'crud/change.html', context={'form': form, 'typ': typ, 'form_error': error_msg, 'nav_dict': nav_dict})

        else:
            return render(request, 'crud/change.html', context={'form': form, 'typ': typ, 'nav_dict': nav_dict})
    else:
        form = form_obj()
        return render(request, 'crud/change.html', context={'form': form, 'typ': typ, 'nav_dict': nav_dict})


@user_passes_test(authorized_to_read, login_url='/denied/')
def UpdateView(request, uid, model_obj, form_obj, typ):
    try:
        old_data = get_object_or_404(model_obj, id=uid)
    except Exception:
        raise Http404('Does Not Exist')

    if request.method == 'POST':
        form = form_obj(request.POST, instance=old_data)

        if form.is_valid():
            form.save()
            return redirect(f'/config/detailed/{typ}/{uid}')

    else:

        form = form_obj(instance=old_data)
        return render(request, 'crud/change.html', context={'form': form, 'typ': typ, 'nav_dict': nav_dict})


@user_passes_test(authorized_to_write, login_url='/denied/')
def DeleteView(request, uid, model_obj, typ, form_obj=None):
    try:
        data = get_object_or_404(model_obj, id=uid)
    except Exception:
        raise Http404('Does Not Exist')

    if request.method == 'POST':
        data.delete()
        return redirect("/config/list/%s/" % typ)
    else:
        raise Http404('Delete only supports post method')
