from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test

from ....user import authorized_to_read, authorized_to_write
from ....config.nav import nav_dict
from ....utils.helper import get_datetime_w_tz, set_key
from ....models import ObjectInputModel, GroupInputModel
from .helper import add_default_chart_options, get_param_if_ok, get_obj_dict, add_graph_params_to_url


class Chart:
    def __init__(self, request, html_template: str, model, form):
        self.request = request
        self.current_path = request.META['PATH_INFO']
        self.html_template = html_template
        self.root_path = 'data/chart'
        self.model = model
        self.form = form

    def get(self, chart_option_defaults: dict):
        self.test_read(self.request)
        data = self.request.GET

        input_device_dict = {instance.name: instance.id for instance in ObjectInputModel.objects.all()}
        input_model_dict = {instance.name: instance.id for instance in GroupInputModel.objects.all()}

        action = get_param_if_ok(data, search='do', choices=['show', 'create'], fallback='show')
        chart_dict = get_obj_dict(request=self.request, typ_model=self.model, typ_form=self.form, action=action, selected='selected')

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

        else:
            return render(self.request, f'{self.root_path}/{self.html_template}.html', context={
                'request': self.request, 'nav_dict': nav_dict, 'input_device_dict': input_device_dict, 'input_model_dict': input_model_dict, 'action': action,
                'form': chart_dict['form'], 'selected': chart_dict['id'], 'object_list': chart_dict['list'],
            })

    def post(self):
        self.test_write(self.request)
        data = self.request.POST

        action = get_param_if_ok(data, search='do', choices=['show', 'create', 'update', 'delete'], fallback='show', lower=True)
        chart_list = self.model.objects.all()
        chart_id = get_param_if_ok(data, search='selected', no_choices=['---------'], format_as=int)
        form = None
        chart_obj = None

        if action in ['delete', 'update']:
            chart_obj = [obj for obj in chart_list if obj.id == int(chart_id)][0]

        if action in ['update', 'create']:

            if action == 'update':
                form = self.form(data, instance=chart_obj)

            else:
                form = self.form(data)

            if form.is_valid():
                form.save()
                return redirect(f'/{self.root_path}/?status={action}d&what={self.html_template}')

        elif action == 'delete':
            chart_obj.delete()
            return redirect(f'/{self.root_path}/?status={action}d&what={self.html_template}')

        return render(self.request, f'{self.root_path}/{self.html_template}.html', context={
            'request': self.request, 'nav_dict': nav_dict, 'form': form, 'action': action, 'selected': chart_id, 'object_list': chart_list,
        })

    @staticmethod
    @user_passes_test(authorized_to_read, login_url='/denied/')
    def test_read(request):
        pass

    @staticmethod
    @user_passes_test(authorized_to_write, login_url='/denied/')
    def test_write(request):
        pass


class Dashboard:
    def __init__(self, request, html_template: str, model, form):
        self.request = request
        self.current_path = request.META['PATH_INFO']
        self.html_template = html_template
        self.root_path = 'data/chart'
        self.model = model
        self.form = form

    def get(self):
        pass

    def post(self):
        pass