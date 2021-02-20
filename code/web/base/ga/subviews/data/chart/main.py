from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

from ....user import authorized_to_read
from ....config.nav import nav_dict
from .helper import get_param_if_ok
from ....forms import ChartGraphModel, ChartDatasetModel, ChartDashboardModel, ChartDatasetForm, ChartGraphForm
from .obj import Chart


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataChartView(request):
    graph_list = ChartGraphModel.objects.all()
    dataset_list = ChartDatasetModel.objects.all()
    dashboard_list = ChartDashboardModel.objects.all()

    status = get_param_if_ok(request.GET, search='status', choices=['updated', 'created', 'deleted'])
    what = get_param_if_ok(request.GET, search='what', choices=['graph', 'dataset'])

    return render(request, 'data/chart/main.html', context={
        'request': request, 'nav_dict': nav_dict, 'status': status, 'what': what, 'graph_list': graph_list, 'dataset_list': dataset_list,
        'dashboard_list': dashboard_list,
    })


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataChartDatasetView(request):
    chart_option_defaults = {
        'chart_fill': True, 'chart_fill_color': 'rgba(100, 185, 215, 0.6)', 'chart_border_color': 'black', 'chart_border_width': 1, 'chart_type': 'line',
        'chart_point_radius': 0, 'chart_point_color': 'blue', 'chart_point_type': 'rectRounded', 'chart_point_hover_radius': 7, 'chart_point_hit_radius': 7,
    }

    if request.method == 'POST':
        return Chart(request, html_template='dataset', form=ChartDatasetForm, model=ChartDatasetModel).post()

    else:
        return Chart(request, html_template='dataset', form=ChartDatasetForm, model=ChartDatasetModel).get(chart_option_defaults)


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataChartGraphView(request):
    chart_option_defaults = {
        'chart_type': 'line', 'time_format_min': 'HH:mm', 'time_format_hour': 'HH:mm | DD-MM-YYYY', 'time_format_day': 'DD-MM-YYYY',
        'time_format_month': 'MM-YYYY', 'chart_x_max_ticks': 15, 'chart_y_max_suggest': None, 'options_json': None,
    }

    if request.method == 'POST':
        return Chart(request, html_template='graph', form=ChartGraphForm, model=ChartGraphModel).post()

    else:
        return Chart(request, html_template='graph', form=ChartGraphForm, model=ChartGraphModel).get(chart_option_defaults)
