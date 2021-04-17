from django.shortcuts import render, redirect
from ast import literal_eval

from ....forms import DashboardModel, DashboardPositionModel, DashboardForm, DashboardPositionForm, ChartDashboardModel, DashboardDefaultModel, DashboardDefaultForm
from ....utils.helper import set_key, get_instance_from_id, empty_key
from ..helper import get_obj_dict, get_param_if_ok
from ....utils.main import error_formatter, method_user_passes_test
from ....submodels.helper.matrix import Matrix
from ....user import authorized_to_read, authorized_to_write

TITLE = 'Dashboard'


class DashboardView:
    def __init__(self, request):
        self.request = request
        self.current_path = request.META['PATH_INFO']
        self.html_template = "data/dashboard/main.html"
        self.model = DashboardModel
        self.form = DashboardForm
        self.root_path = 'data/dashboard'
        self.initiator = None

    @method_user_passes_test(authorized_to_read, login_url='/accounts/login/')
    def go_config(self, info: str = None):
        self.initiator = 'config'
        self.html_template = "data/dashboard/config.html"
        self.root_path = 'data/dashboard/config'
        if self.request.method == 'POST':
            return self._post(info=info)

        else:
            if info is not None:
                redirect(f'/{self.root_path}/?form_error={info}+does+only+support+POST+method')

            return self._get()

    @method_user_passes_test(authorized_to_read, login_url='/accounts/login/')
    def go_main(self):
        self.initiator = 'main'
        if self.request.method == 'POST':
            return self._post()

        else:
            return self._get()

    def _get(self):
        data = self.request.GET
        action = get_param_if_ok(data, search='do', choices=['show', 'create', 'update'], fallback='show', lower=True)
        db_dict, default_db = self._get_config()

        if self.initiator == 'main':
            # redirect to config
            if action in ['create', 'update']:
                addition = ''

                if db_dict['id'] is not None and action == 'update':
                    addition = f"?selected={db_dict['id']}&do={action}"

                elif action == 'create':
                    addition = f'?do={action}'

                return redirect(f'/data/dashboard/config/{addition}')

            # redirect with selected
            elif empty_key(data, 'selected') and default_db is not None:
                return redirect(f'/data/dashboard/?selected={default_db}')

        dbe_list = ChartDashboardModel.objects.all()
        position_list = DashboardPositionModel.objects.all()

        status = get_param_if_ok(self.request.GET, search='status', choices=['updated', 'created', 'deleted'])
        free_positions = []
        used_positions = {}
        selected_dbe_ids = []
        form_error = None
        grid_areas = ''
        grid_free_positions = []

        if set_key(data, 'form_error'):
            form_error = data['form_error']

        if db_dict['obj'] is not None:
            _obj = db_dict['obj']
            matrix = Matrix(matrix=_obj.matrix)
            free_positions, position_used = matrix.free({'y0': 1, 'y1': _obj.rows, 'x0': 1, 'x1': _obj.columns}, used=True, both=True)

            # Config for css matrix-grid
            grid_item_free = "ga_dbp_filler_%s"
            grid_item_used_tmpl = "ga_dbp_%s"
            grid_areas = ''
            grid_item_free_count = 0
            for row in range(1, db_dict['obj'].rows + 1):
                _cols = ["'"]
                for col in range(1, db_dict['obj'].columns + 1):
                    if {'y': row, 'x': col} in free_positions:
                        grid_item_free_count += 1
                        grid_free_positions.append({'y': row, 'x': col, 'count': grid_item_free_count})

                        if self.initiator == 'config':
                            _cols.append(grid_item_free % grid_item_free_count)

                        else:
                            _cols.append('.')

                    else:
                        try:
                            dbp_id = [dbe['value'] for dbe in position_used if dbe['x'] == col and dbe['y'] == row][0]
                            _cols.append(grid_item_used_tmpl % dbp_id)
                            dbp_obj = get_instance_from_id(typ=DashboardPositionModel, obj=dbp_id)

                            if dbp_obj is not None:
                                used_positions[dbp_obj] = 'NonDuplicationWA'

                        except IndexError:
                            continue

                _cols.append("' ")
                grid_areas = grid_areas + ' '.join(_cols)

        return render(self.request, self.html_template, context={
            'request': self.request, 'action': action, 'db_dict': db_dict, 'dbe_list': dbe_list, 'default_db': default_db,
            'status': status, 'position_list': position_list, 'selected_dbe_ids': selected_dbe_ids, 'free_positions': free_positions,
            'form_error': form_error, 'grid_areas': grid_areas, 'used_positions': list(used_positions.keys()), 'grid_free_positions': grid_free_positions,
            'default': default_db, 'title': TITLE,
        })

    @method_user_passes_test(authorized_to_write, login_url='/accounts/login/')
    def _post(self, info: str = None):
        data = self.request.POST
        action = get_param_if_ok(data, search='do', choices=['create', 'update', 'delete'], fallback='update', lower=True)
        db_dict, default_db = self._get_config()

        if info == 'dp':
            db_dict = get_obj_dict(request=self.request, typ_model=self.model, typ_form=self.form, selected='dashboard')
            redirect_url = f"/{self.root_path}/?status=updated&do=show&selected={db_dict['id']}"
            post_form = DashboardPositionForm

            if action == 'create':
                xy_begin = literal_eval(data['begin'])
                xy_end = literal_eval(data['end'])
                data = data.copy()
                data['x0'] = xy_begin['x']
                data['y0'] = xy_begin['y']
                data['x1'] = xy_end['x']
                data['y1'] = xy_end['y']

            else:
                db_dict = get_obj_dict(request=self.request, typ_model=DashboardPositionModel, typ_form=post_form, selected='selected')

        else:
            post_form = self.form
            redirect_url = f'/{self.root_path}/?status={action}d&do=show'

        if self.initiator == 'main' and set_key(data, 'default'):
            post_form = DashboardDefaultForm
            db_dict = get_obj_dict(request=self.request, typ_model=DashboardDefaultModel, typ_form=post_form, selected='default')

        if db_dict['id'] is not None and action != 'delete' and self.initiator == 'config':
            redirect_url = redirect_url + f"&selected={db_dict['id']}"

        redirect_url = self._remove_form_error(url=redirect_url)

        if action in ['delete', 'update'] and db_dict['obj'] is None:
            action = 'create'

        if action in ['update', 'create']:

            if action == 'update':
                form = post_form(data, instance=db_dict['obj'])

            else:
                form = post_form(data)

            if form.is_valid():
                _obj = form.save()

                if post_form == self.form and redirect_url.find('selected') == -1:
                    redirect_url = redirect_url + f"&selected={_obj.id}"

                return redirect(redirect_url)

            else:
                # log error or whatever
                error = error_formatter(form.errors)
                return redirect(self._add_form_error(url=redirect_url, error=error))

        elif action == 'delete':
            db_dict['obj'].delete()
            return redirect(redirect_url)

        return render(self.request, self.html_template, context={
            'request': self.request, 'action': action, 'db_dict': db_dict, 'dbe_list': db_dict['list'], 'default_db': default_db, 'title': TITLE,
        })

    def _get_config(self) -> tuple:
        db_dict = get_obj_dict(request=self.request, typ_model=self.model, typ_form=self.form, selected='selected')

        default_db = None
        for default in DashboardDefaultModel.objects.all():
            if default.user == self.request.user:
                default_db = default.dashboard.id

        return db_dict, default_db

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
