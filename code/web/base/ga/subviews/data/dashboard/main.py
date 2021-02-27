from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

from ....user import authorized_to_read, authorized_to_write
from ....config.nav import nav_dict
from ....forms import DashboardModel, DashboardPositionModel, DashboardForm, DashboardPositionForm, ChartDashboardModel, DashboardDefaultModel
from ....utils.helper import get_instance_from_id
from ..helper import get_obj_dict, get_param_if_ok


class DashboardView:
    def __init__(self, request):
        self.request = request
        self.current_path = request.META['PATH_INFO']
        self.html_template = "data/dashboard/main.html"
        self.model = DashboardModel
        self.form = DashboardForm

    def go(self):
        self.test_read(self.request)
        if self.request.method == 'POST':
            return self.post()

        else:
            return self.get()

    def get(self):
        data = self.request.GET
        action = get_param_if_ok(data, search='do', choices=['show', 'create'], fallback='show', lower=True)
        db_dict = get_obj_dict(request=self.request, typ_model=self.model, typ_form=self.form, action=action, selected='db')
        dbe_list = ChartDashboardModel.objects.all()

        default_db = None
        for default in DashboardDefaultModel.objects.all():
            if default.user == self.request.user:
                default_db = default.dashboard

        if action == 'show':
            pass

        return render(self.request, self.html_template, context={
            'request': self.request, 'nav_dict': nav_dict, 'action': action, 'db_dict': db_dict, 'dbe_list': dbe_list, 'default_db': default_db,
        })

    def post(self):
        self.test_write(self.request)
        data = self.request.POST
        action = get_param_if_ok(data, search='do', choices=['create', 'update', 'delete'], fallback='update', lower=True)



    @staticmethod
    @user_passes_test(authorized_to_read, login_url='/denied/')
    def test_read(request):
        pass

    @staticmethod
    @user_passes_test(authorized_to_write, login_url='/denied/')
    def test_write(request):
        pass
