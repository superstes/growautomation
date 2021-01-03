from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test

from ....user import authorized_to_read
from ....config.nav import nav_dict
from ....models import ObjectInputModel, GroupInputModel
from ....utils.helper import get_datetime_w_tz, get_form_prefill
from ....utils.main import get_as_string
from ....forms import ChartForm, ChartLinkForm, ChartDatasetForm


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataChartView(request):

    return render(request, 'data/chart/dashboard.html', context={
        'request': request, 'nav_dict': nav_dict,
    })


def add_ds_chart_options(request, defaults: dict, redirect_path: str):
    out_dict = {}

    for key, value in request.GET.items():
        out_dict[key] = value

    for key, value in defaults.items():
        if key not in request.GET or request.GET[key] is None:
            out_dict[key] = value

    return redirect("%s/%s" % (redirect_path, get_as_string(out_dict)))


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataChartDatasetView(request):
    input_device_dict = {instance.name: instance.id for instance in ObjectInputModel.objects.all()}
    input_model_dict = {instance.name: instance.id for instance in GroupInputModel.objects.all()}

    chart_option_defaults = {
        'chart_fill': True, 'chart_fill_color': 'rgba(100, 185, 215, 0.6)', 'chart_border_color': 'black', 'chart_border_width': 1, 'chart_type': None,
        'chart_point_radius': 0, 'chart_point_color': 'blue', 'chart_point_type': 'rectRounded', 'chart_point_hover_radius': 7, 'chart_point_hit_radius': 7,
    }

    form = ChartDatasetForm(initial=get_form_prefill(request))

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

    for key in chart_option_defaults.keys():
        if key not in request.GET:
            return add_ds_chart_options(request, defaults=chart_option_defaults, redirect_path='/data/chart/dataset')

    return render(request, 'data/chart/dataset.html', context={
        'request': request, 'nav_dict': nav_dict, 'input_device_dict': input_device_dict, 'start_ts': start_ts, 'stop_ts': stop_ts, 'input_device': input_device,
        'form': form, 'input_model_dict': input_model_dict,
    })


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataChartGraphView(request):
    input_device_dict = {instance.name: instance.id for instance in ObjectInputModel.objects.all()}
    input_model_dict = {instance.name: instance.id for instance in GroupInputModel.objects.all()}

    chart_option_defaults = {
        'chart_type': 'line', 'time_format_min': 'HH:mm', 'time_format_hour': 'HH:mm | DD-MM-YYYY', 'time_format_day': 'DD-MM-YYYY', 'time_format_month': 'MM-YYYY',
        'chart_x_max_ticks': 15, 'chart_y_max_suggest': None, 'options_json': None,
    }

    form = ChartForm(initial=get_form_prefill(request))

    for key in chart_option_defaults.keys():
        if key not in request.GET:
            return add_ds_chart_options(request, defaults=chart_option_defaults, redirect_path='/data/chart/graph')

    return render(request, 'data/chart/graph.html', context={
        'request': request, 'nav_dict': nav_dict, 'input_device_dict': input_device_dict, 'input_model_dict': input_model_dict, 'form': form,
    })
