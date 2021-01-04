from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test

from ....user import authorized_to_read
from ....config.nav import nav_dict
from .helper import get_param_if_ok
from ....models import ChartGraphModel, ChartDatasetModel


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataChartDashboardView(request):
    graph_list = ChartGraphModel.objects.all()
    dataset_list = ChartDatasetModel.objects.all()

    status = get_param_if_ok(request.GET, search='status', choices=['updated', 'created', 'deleted'])
    what = get_param_if_ok(request.GET, search='what', choices=['graph prototype', 'dataset'])

    return render(request, 'data/chart/dashboard.html', context={
        'request': request, 'nav_dict': nav_dict, 'status': status, 'what': what, 'graph_list': graph_list, 'dataset_list': dataset_list,
    })
