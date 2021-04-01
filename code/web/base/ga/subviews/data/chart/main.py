from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

from ....user import authorized_to_read
from ..helper import get_param_if_ok
from ....forms import ChartGraphModel, ChartDatasetModel, ChartDatasetForm, ChartGraphForm, ChartDashboardModel, ChartDashboardForm
from ....forms import ChartDatasetLinkModel, ChartDatasetLinkForm, ChartGraphLinkModel, ChartGraphLinkForm
from .obj import Chart


dbe_path = '/data/chart/dbe'
TITLE = 'Data charts'


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataChartView(request):
    graph_list = ChartGraphModel.objects.all()
    dataset_list = ChartDatasetModel.objects.all()
    dashboard_list = ChartDashboardModel.objects.all()

    status = get_param_if_ok(request.GET, search='status', choices=['updated', 'created', 'deleted'])
    what = get_param_if_ok(request.GET, search='what', choices=['graph', 'dataset', 'dbe'])

    return render(request, 'data/chart/main.html', context={
        'request': request, 'status': status, 'what': what, 'graph_list': graph_list, 'dataset_list': dataset_list,
        'dashboard_list': dashboard_list, 'title': TITLE,
    })


def DataChartDatasetView(request):
    chart_option_defaults = {
        'chart_fill': True, 'chart_fill_color': 'rgba(100, 185, 215, 0.6)', 'chart_border_color': 'black', 'chart_border_width': 1, 'chart_type': 'line',
        'chart_point_radius': 0, 'chart_point_color': 'blue', 'chart_point_type': 'rectRounded', 'chart_point_hover_radius': 7, 'chart_point_hit_radius': 7,
        'title': TITLE,
    }

    return Chart(request, html_template='dataset', form=ChartDatasetForm, model=ChartDatasetModel).go(chart_option_defaults)


def DataChartGraphView(request):
    chart_option_defaults = {
        'chart_type': 'line', 'time_format_min': 'HH:mm', 'time_format_hour': 'HH:mm | DD-MM-YYYY', 'time_format_day': 'DD-MM-YYYY',
        'time_format_month': 'MM-YYYY', 'chart_x_max_ticks': 15, 'chart_y_max_suggest': None, 'options_json': None, 'title': TITLE,
    }

    return Chart(request, html_template='graph', form=ChartGraphForm, model=ChartGraphModel).go(chart_option_defaults)


def DataChartDbeView(request):
    return Chart(request, html_template='dbe', form=ChartDashboardForm, model=ChartDashboardModel).go({})


def DataChartDbeDatasetView(request):
    return Chart(request, html_template='dbe', form=ChartDatasetLinkForm, model=ChartDatasetLinkModel).go({})


def DataChartDbeGraphView(request):
    return Chart(request, html_template='dbe', form=ChartGraphLinkForm, model=ChartGraphLinkModel).go({})

