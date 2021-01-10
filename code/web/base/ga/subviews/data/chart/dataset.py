from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test

from ....user import authorized_to_read, authorized_to_write
from ....config.nav import nav_dict
from ....models import ObjectInputModel, GroupInputModel
from ....utils.helper import get_datetime_w_tz, get_form_prefill
from ....forms import ChartDatasetForm, ChartDatasetModel
from ...handlers import handler404
from .helper import add_ds_chart_options, get_param_if_ok, get_obj_dict


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataChartDatasetView(request):
    input_device_dict = {instance.name: instance.id for instance in ObjectInputModel.objects.all()}
    input_model_dict = {instance.name: instance.id for instance in GroupInputModel.objects.all()}

    chart_option_defaults = {
        'chart_fill': True, 'chart_fill_color': 'rgba(100, 185, 215, 0.6)', 'chart_border_color': 'black', 'chart_border_width': 1, 'chart_type': None,
        'chart_point_radius': 0, 'chart_point_color': 'blue', 'chart_point_type': 'rectRounded', 'chart_point_hover_radius': 7, 'chart_point_hit_radius': 7,
    }

    if request.method == 'POST':
        return _write(request)

    else:
        for key in chart_option_defaults.keys():
            if key not in request.GET:
                return add_ds_chart_options(request, defaults=chart_option_defaults, redirect_path='/data/chart/dataset')

        action = get_param_if_ok(request.GET, search='do', choices=['show', 'create', 'update', 'delete'], fallback='show')

        graph_dict = get_obj_dict(request=request, typ_model=ChartDatasetModel, typ_form=ChartDatasetForm, action=action, selected='selected')

        stop_ts = None
        start_ts = None
        input_device = None

        # todo: either input_device or input_model

        if 'input_device' in request.GET:
            input_device = request.GET['input_device']

        if 'start_ts' in request.GET:
            start_ts = get_datetime_w_tz(request, dt_str=request.GET['start_ts'])

            if 'stop_ts' in request.GET:
                _stop_ts = get_datetime_w_tz(request, dt_str=request.GET['stop_ts'])

                if _stop_ts is not None:
                    if _stop_ts > start_ts:
                        stop_ts = _stop_ts

        return render(request, 'data/chart/dataset.html', context={
            'request': request, 'nav_dict': nav_dict, 'input_device_dict': input_device_dict, 'start_ts': start_ts, 'stop_ts': stop_ts, 'input_device': input_device,
            'input_model_dict': input_model_dict, 'action': action, 'selected': graph_dict['id'], 'form': graph_dict['form'], 'object_list': graph_dict['list'],
        })


@user_passes_test(authorized_to_write, login_url='/denied/')
def _write(request):
    action = get_param_if_ok(request.POST, search='do', choices=['show', 'create', 'update', 'delete'], fallback='show')
    dataset_list = ChartDatasetModel.objects.all()
    dataset = get_param_if_ok(request.GET, search='selected', no_choices=['---------'], format_as=int)
    if action in ['delete', 'update']:
        dataset_obj = [obj for obj in dataset_list if obj.id == int(dataset)][0]

    if action in ['update', 'create']:

        if action == 'update':
            form = ChartDatasetForm(request.POST, instance=dataset_obj)
        else:
            form = ChartDatasetForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect(f'/data/chart/?status={action}d&what=dataset')

    elif action == 'delete':
        dataset_obj.delete()
        return redirect(f'/data/chart/?status={action}d&what=dataset')

    return render(request, 'data/chart/dataset.html', context={
            'request': request, 'nav_dict': nav_dict, 'form': form, 'action': action, 'selected': dataset, 'object_list': dataset_list,
        })

