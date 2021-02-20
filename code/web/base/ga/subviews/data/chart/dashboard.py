from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test

from ....user import authorized_to_read, authorized_to_write
from ....config.nav import nav_dict
from .helper import get_param_if_ok, get_obj_dict, get_existing_params_dict, add_graph_params_to_url
from ....forms import ChartDatasetLinkModel, ChartGraphLinkModel, ChartDatasetLinkForm, ChartGraphLinkForm, ChartDashboardForm, ChartDashboardModel
from ...handlers import handler404
from ....utils.helper import get_form_prefill, get_instance_from_id, empty_key
from ....utils.main import get_as_string


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataChartDashboardView(request):
    tmpl = 'data/chart/dashboard.html'
    graph_link_list = ChartGraphLinkModel.objects.all()
    dashboard_list = ChartDashboardModel.objects.all()
    dataset_link_list = []
    dataset_id_list = []
    graph_id = None
    current_path = request.META['PATH_INFO']

    action = get_param_if_ok(request.GET, search='do', choices=['show', 'create'], fallback='show')

    dashboard_dict = get_obj_dict(request=request, typ_model=ChartDashboardModel, typ_form=ChartDashboardForm, action=action, selected='selected')

    # set chart params if one is selected
    add_param_redirect = add_graph_params_to_url(request, chart_dict=dashboard_dict, redirect_path=current_path)

    if add_param_redirect is not None:
        return add_param_redirect

    graph_dict = {'id': None, 'form': ChartGraphLinkForm(request.GET, initial=get_form_prefill(request))}

    if dashboard_dict['id'] is not None:
        for obj in ChartDatasetLinkModel.objects.all():
            if obj.group.id == int(dashboard_dict['id']):
                dataset_link_list.append(obj)
                dataset_id_list.append(obj.obj.id)

        for obj in graph_link_list:
            if obj.group.id == int(dashboard_dict['id']):
                graph_dict = get_obj_dict(request=request, typ_model=ChartGraphLinkModel, typ_form=ChartGraphLinkForm, action=action, selected_id=obj.id)
                graph_id = obj.obj.id

    if 'dataset' not in request.GET and 'graph' not in request.GET:
        current_url = request.get_full_path()

        if len(dataset_id_list) != 0:
            dataset_str = '&'

            for ds_id in dataset_id_list:
                dataset_str = "%s&dataset=%s" % (dataset_str, ds_id)

        else:
            dataset_str = ''

        return redirect("%s&graph=%s%s" % (current_url, graph_id, dataset_str))

    render_context = {
        'request': request, 'nav_dict': nav_dict, 'action': action, 'form': dashboard_dict['form'], 'selected': dashboard_dict['id'],
        'graph_form': graph_dict['form'], 'graph_selected': graph_dict['id'], 'dataset_link_list': dataset_link_list, 'object_list': dashboard_list,
    }

    if request.method == 'POST':
        if 'form' in request.POST:
            form_type = request.POST['form']
            if form_type == 'graph':
                link_obj = get_instance_from_id(typ=ChartGraphLinkModel, obj=request.POST['id'], force_id=True)

                if link_obj in graph_link_list:
                    form = ChartGraphLinkForm(request.POST, instance=link_obj)

                else:
                    form = ChartGraphLinkForm(request.POST)

            else:
                return render(request, tmpl, context=render_context)

        else:
            form = ChartDashboardForm(request.POST)

        if form.is_valid():
            return _save_form(request=request, form=form, tmpl=tmpl)

        else:
            render_context.update({'form_error': form.errors})
            return render(request, tmpl, context=render_context)

    else:
        return render(request, tmpl, context=render_context)


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataChartDatasetLinkView(request):
    tmpl = 'data/chart/link_dataset.html'

    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST['action']
        else:
            action = 'Create'

        form = ChartDatasetLinkForm(request.POST)

        if action == 'Delete':
            _id = request.POST['id']
            try:
                link_obj = get_object_or_404(ChartDatasetLinkModel, id=_id)
            except Exception:
                raise handler404(request, msg='Does Not Exist')

            if request.method == 'POST':
                link_obj.delete()
                return get_redirect(request)

            else:
                raise handler404(request, msg='Delete only supports post method')

        else:
            if form.is_valid():
                return _save_form(request=request, form=form, tmpl=tmpl)

            else:
                return render(request, tmpl, context={'form': form, 'nav_dict': nav_dict})
    else:
        form = ChartDatasetLinkForm()
        return render(request, tmpl, context={'form': form, 'nav_dict': nav_dict})


@user_passes_test(authorized_to_write, login_url='/denied/')
def _save_form(request, form, tmpl: str):
    try:
        form.save()
        return get_redirect(request)

    except ValueError as error_msg:
        return render(request, tmpl, context={'form': form, 'form_error': error_msg, 'nav_dict': nav_dict})


def get_redirect(request):
    post_dict = get_existing_params_dict(request.POST)
    get_dict = get_existing_params_dict(request.GET)

    if empty_key(get_dict, param='return'):
        return redirect("/data/chart/dashboard/%s" % get_as_string({**get_dict, **post_dict}))

    else:
        return redirect(get_dict['return'])
