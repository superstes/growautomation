from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test

from ....user import authorized_to_read, authorized_to_write
from ....config.nav import nav_dict
from ....models import ObjectInputModel, GroupInputModel
from ....utils.helper import get_form_prefill
from ....forms import ChartGraphForm, ChartGraphModel
from ...handlers import handler404
from .helper import add_ds_chart_options, get_param_if_ok


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataChartGraphView(request):
    input_device_dict = {instance.name: instance.id for instance in ObjectInputModel.objects.all()}
    input_model_dict = {instance.name: instance.id for instance in GroupInputModel.objects.all()}

    chart_option_defaults = {
        'chart_type': 'line', 'time_format_min': 'HH:mm', 'time_format_hour': 'HH:mm | DD-MM-YYYY', 'time_format_day': 'DD-MM-YYYY', 'time_format_month': 'MM-YYYY',
        'chart_x_max_ticks': 15, 'chart_y_max_suggest': None, 'options_json': None,
    }

    if request.method == 'POST':
        return _write(request)

    else:
        for key in chart_option_defaults.keys():
            if key not in request.GET:
                return add_ds_chart_options(request, defaults=chart_option_defaults, redirect_path='/data/chart/graph')

        action = get_param_if_ok(request.GET, search='do', choices=['show', 'create', 'update', 'delete'])

        graph = get_param_if_ok(request.GET, search='selected', no_choices=['---------'], format_as=int)
        graph_obj = None
        graph_list = None

        if action in ['update', 'show', 'delete']:
            graph_list = ChartGraphModel.objects.all()
            if graph:
                graph_obj = [obj for obj in graph_list if obj.id == graph][0]

        if graph_obj:
            form = ChartGraphForm(instance=graph_obj)
        else:
            form = ChartGraphForm(request.GET, initial=get_form_prefill(request))

        return render(request, 'data/chart/graph.html', context={
            'request': request, 'nav_dict': nav_dict, 'input_device_dict': input_device_dict, 'input_model_dict': input_model_dict, 'form': form, 'action': action,
            'selected': graph, 'object_list': graph_list,
        })


@user_passes_test(authorized_to_write, login_url='/denied/')
def _write(request):
    action = get_param_if_ok(request.POST, search='do', choices=['show', 'create', 'update', 'delete'])
    graph_list = ChartGraphModel.objects.all()
    graph = get_param_if_ok(request.GET, search='selected', no_choices=['---------'], format_as=int)
    if action in ['delete', 'update']:
        graph_obj = [obj for obj in graph_list if obj.id == int(graph)][0]

    if action in ['update', 'create']:

        if action == 'update':
            form = ChartGraphForm(request.POST, instance=graph_obj)
        else:
            form = ChartGraphForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect(f'/data/chart/?status={action}d&what=graph+prototype')

    elif action == 'delete':
        graph_obj.delete()
        return redirect(f'/data/chart/?status={action}d&what=graph+prototype')

    return render(request, 'data/chart/graph.html', context={
            'request': request, 'nav_dict': nav_dict, 'form': form, 'action': action, 'selected': graph, 'object_list': graph_list,
        })
