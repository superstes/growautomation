from django.shortcuts import render, redirect

from ....config.nav import nav_dict
from ....utils.helper import get_datetime_w_tz, set_key, get_form_prefill
from ....forms import ObjectInputModel, GroupInputModel, ChartGraphLinkModel, ChartDatasetLinkModel, ChartGraphLinkForm, ChartDatasetModel
from ..helper import add_default_chart_options, get_param_if_ok, get_obj_dict, add_graph_params_to_url
from ....utils.main import test_read, test_write, error_formatter


class Chart:
    def __init__(self, request, html_template: str, model, form):
        self.request = request
        self.current_path = request.META['PATH_INFO']
        self.html_template = html_template
        self.root_path = 'data/chart'
        self.model = model
        self.form = form

    def go(self, chart_option_defaults: dict):
        if self.request.method == 'POST':
            return self.post()

        else:
            return self.get(chart_option_defaults)

    def get(self, chart_option_defaults: dict):
        test_read(self.request)
        data = self.request.GET

        input_device_dict = {instance.name: instance.id for instance in ObjectInputModel.objects.all()}
        input_model_dict = {instance.name: instance.id for instance in GroupInputModel.objects.all()}

        action = get_param_if_ok(data, search='do', choices=['show', 'create'], fallback='show')
        chart_dict = get_obj_dict(request=self.request, typ_model=self.model, typ_form=self.form, selected='selected')

        # set chart params if one is selected
        add_param_redirect = add_graph_params_to_url(self.request, chart_dict=chart_dict, redirect_path=self.current_path)

        if add_param_redirect is not None:
            return add_param_redirect

        # override chart params with defaults if they are not existent or empty
        add_param_redirect = add_default_chart_options(self.request, defaults=chart_option_defaults, redirect_path=self.current_path)

        if add_param_redirect is not None:
            return add_param_redirect

        if self.html_template == 'dataset':
            stop_ts = None
            start_ts = None
            input_device = None

            # todo: either input_device or input_model

            if set_key(data, param='input_device'):
                input_device = data['input_device']

            if set_key(data, param='start_ts'):
                start_ts = get_datetime_w_tz(self.request, dt_str=data['start_ts'])

                if set_key(data, param='stop_ts'):
                    _stop_ts = get_datetime_w_tz(self.request, dt_str=data['stop_ts'])

                    if _stop_ts is not None:
                        if _stop_ts > start_ts:
                            stop_ts = _stop_ts

            return render(self.request, f'{self.root_path}/{self.html_template}.html', context={
                'request': self.request, 'nav_dict': nav_dict, 'input_device_dict': input_device_dict, 'start_ts': start_ts, 'stop_ts': stop_ts,
                'input_device': input_device, 'input_model_dict': input_model_dict, 'action': action, 'selected': chart_dict['id'], 'form': chart_dict['form'],
                'object_list': chart_dict['list'],
            })

        elif self.html_template == 'dbe':
            dataset_list = ChartDatasetModel.objects.all()
            dataset_link_list = ChartDatasetLinkModel.objects.all()
            graph_link_list = ChartGraphLinkModel.objects.all()
            selected_dataset_ids = []
            form_error = data['form_error'] if set_key(data, param='form_error') else None
            graph_form = ChartGraphLinkForm(data, initial=get_form_prefill(self.request))

            if set_key(chart_dict, 'obj'):
                try:
                    link_obj = [link for link in graph_link_list if link.group.id == int(chart_dict['id'])][0]
                    graph_form = ChartGraphLinkForm(instance=link_obj)
                    for dataset_link in dataset_link_list:
                        if dataset_link.group.id == int(chart_dict['id']):
                            selected_dataset_ids.append(dataset_link.obj.id)

                except IndexError:
                    pass

            return render(self.request, f'{self.root_path}/{self.html_template}.html', context={
                'request': self.request, 'nav_dict': nav_dict, 'input_device_dict': input_device_dict, 'input_model_dict': input_model_dict, 'action': action,
                'form': chart_dict['form'], 'selected': chart_dict['id'], 'object_list': chart_dict['list'], 'selected_dataset_ids': selected_dataset_ids,
                'dataset_link_list': dataset_link_list, 'graph_link_list': graph_link_list, 'dataset_list': dataset_list, 'graph_form': graph_form,
                'form_error': form_error
            })

        else:

            return render(self.request, f'{self.root_path}/{self.html_template}.html', context={
                'request': self.request, 'nav_dict': nav_dict, 'input_device_dict': input_device_dict, 'input_model_dict': input_model_dict, 'action': action,
                'form': chart_dict['form'], 'selected': chart_dict['id'], 'object_list': chart_dict['list'],
            })

    def post(self):
        test_write(self.request)
        data = self.request.POST

        action = get_param_if_ok(data, search='do', choices=['create', 'update', 'delete'], fallback='update', lower=True)
        chart_list = self.model.objects.all()
        chart_id = get_param_if_ok(data, search='selected', no_choices=['---------'], format_as=int)
        form = None
        chart_obj = None
        redirect_url = f'/{self.root_path}/?status={action}d&what={self.html_template}'

        if set_key(data, param='return'):
            redirect_url = data['return']

        redirect_url = self._remove_form_error(url=redirect_url)

        if action in ['delete', 'update']:
            try:
                try:
                    chart_obj = [link for link in chart_list if link.id == int(chart_id)][0]

                except TypeError:
                    chart_obj = [link for link in chart_list if link.group.id == int(data['group'])][0]

            except (IndexError, KeyError, TypeError) as error:
                # log error or whatever
                action = 'create'

        if action in ['update', 'create']:

            if action == 'update':
                form = self.form(data, instance=chart_obj)

            else:
                form = self.form(data)

            if form.is_valid():
                _obj = form.save()

                if self.html_template == 'dbe' and action == 'create' and redirect_url.find('selected') == -1:
                    redirect_url = f'/{self.root_path}/dbe/?selected={_obj.id}&do=show'

                return redirect(redirect_url)

            else:
                # log error or whatever
                error = error_formatter(form.errors)

                return redirect(self._add_form_error(url=redirect_url, error=error))

        elif action == 'delete':
            chart_obj.delete()
            return redirect(redirect_url)

        return render(self.request, f'{self.root_path}/{self.html_template}.html', context={
            'request': self.request, 'nav_dict': nav_dict, 'form': form, 'action': action, 'selected': chart_id, 'object_list': chart_list,
        })

    def _add_form_error(self, url: str, error: str = 'Failed+to+save+form'):
        if set_key(self.request.GET, 'form_error'):
            return url

        else:
            if url.find('?') == -1:
                return "%s?form_error=%s" % (url, error)

            return "%s&form_error=%s" % (url, error)

    @staticmethod
    def _remove_form_error(url: str, error: str = 'Failed+to+save+form'):
        return url.replace("&form_error=%s" % error, '')
