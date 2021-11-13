from django.shortcuts import render, get_object_or_404, redirect

from ...forms import LABEL_DICT, HELP_DICT
from ...subviews.handlers import Pseudo404
from ...utils.auth import method_user_passes_test
from ...utils.web import redirect_if_hidden
from ...config.site import MAIN_CONFIG, MEMBER_CONFIG
from ...utils.helper import member_pre_process
from ...user import authorized_to_read, authorized_to_write
from ...utils.basic import set_key
from ...config.shared import CENSOR_STRING, LOGIN_URL, WEBUI_SOCKET_INFO_TIMEOUT
from ..api.sock.main import api_sock


class ConfigView:
    def __init__(self, request, typ: str, action: str, uid: (str, int) = None, sub_type: str = None):
        self.request = request
        self.action = action
        self.type = typ
        self.uid = uid
        self.sub_type = sub_type
        self.tmpl_root = 'config'

        try:
            self.title = f"{MAIN_CONFIG[self.type]['pretty']}"

        except KeyError:
            self.title = 'Config'

        if self.type in MAIN_CONFIG and 'redirect' in MAIN_CONFIG[self.type]:
            post_target = MAIN_CONFIG[self.type]['redirect']

        else:
            post_target = self.type

        if 'next' in request.GET:
            self.post_redirect = request.GET['next']

        elif 'HTTP_REFERER' in request.META:
            self.post_redirect = request.META['HTTP_REFERER']

        else:
            self.post_redirect = f'/{self.tmpl_root}/list/{post_target}/'

        self.error_msgs = {
            'id': f"Item with id {self.uid} does not exist",
            'method': f"Action '{self.action}' not supported for current method",
            'type': f"Data type '{self.type}' does not exist",
        }
        self.model, self.form = None, None
        self.data = request.GET

    def go(self):
        self._set_model_form()
        hidden_redirect = self._check_hidden()
        if hidden_redirect is not None:
            return hidden_redirect

        if self.request.method == 'POST':
            self.data = self.request.POST
            return self._post()

        else:
            return self._get()

    @method_user_passes_test(authorized_to_read, login_url=LOGIN_URL)
    def _get(self):
        if self.action == 'list':
            tmpl, context = self._get_list()

        elif self.action == 'detailed':
            tmpl, context = self._get_detail()

        elif self.action == 'update':
            tmpl, context = self._get_update()

        elif self.action == 'create':
            tmpl, context = self._get_create()

        elif self.action == 'switch':
            return self._get_switch()

        else:
            raise Pseudo404(ga={'request': self.request, 'msg': self.error_msgs['method']})

        return render(self.request, f'{self.tmpl_root}/{tmpl}.html', context=context)

    @method_user_passes_test(authorized_to_write, login_url=LOGIN_URL)
    def _post(self):
        if self.action == 'update':
            return self._post_update()

        elif self.action == 'delete':
            return self._post_delete()

        elif self.action == 'create':
            return self._post_create()

        else:
            raise Pseudo404(ga={'request': self.request, 'msg': self.error_msgs['method']})

    def _set_model_form(self):
        if self.type in MAIN_CONFIG:
            self.form = MAIN_CONFIG[self.type]['form']
            self.model = MAIN_CONFIG[self.type]['model']

        else:
            raise Pseudo404(ga={'request': self.request, 'msg': self.error_msgs['type']})

    def _check_hidden(self):
        if MAIN_CONFIG[self.type]['hidden'] is True and self.action == 'list':
            return redirect_if_hidden(request=self.request, target=MAIN_CONFIG[self.type]['redirect'])

    def _get_switch(self):
        """
        will care for complexer request-switching
        used for member-action (add/create/list) forms
        """
        switch_action = self.data['action'].lower()
        switch_type = self.type
        switch_sub_type = self.sub_type
        default_switch_sub_type = 'object'
        params = '?action=Create'
        member_config = MEMBER_CONFIG[self.type]

        try:
            if switch_action in ['create', 'list']:
                if switch_sub_type in member_config:
                    switch_type = member_config[switch_sub_type]['url']

                else:
                    switch_sub_type = default_switch_sub_type
                    switch_type = member_config[default_switch_sub_type]['url']

            if switch_action == 'add':
                switch_action = 'create'

                if switch_sub_type in member_config:
                    if set_key(member_config[switch_sub_type], 'add_url'):
                        switch_type = member_config[switch_sub_type]['add_url']

                params = f"?group={self.data['group']}&member_type={switch_sub_type}&group_type={self.type}&action=Add"

            return redirect(f"/{self.tmpl_root}/{switch_action}/{switch_type}/{params}")

        except KeyError:
            return redirect(self.post_redirect)

    def _get_list(self):
        dataset = self.model.objects.all()
        context, member_type, member_data, member_config, device_status = None, None, None, None, None
        # group_tbl and member_tbl should be the same length
        #   '': '' can be used for empty columns
        # special table contents:
        #   ! => pull following key from MEMBER_CONFIG
        #   ? => pull following key from member object
        if self.request.user_agent.is_mobile:
            group_tbl = {'name': 'name', 'enabled': 'enabled'}
            member_tbl = {'type': '!pretty', 'name': 'name', 'enabled': 'enabled'}

        else:
            group_tbl = {'name': 'name', 'description': 'description', 'enabled': 'enabled'}
            member_tbl = {'type': '!pretty', 'name': 'name', 'description': 'description', 'enabled': 'enabled'}

        if self.type == 'conditiongroup':
            member_type = 'conditionmember'
            member_config = MEMBER_CONFIG[member_type]
            member_data = {
                'condition_member_link': member_config['condition_member_link']['model'].objects.all(),
                'condition_member_output': member_config['condition_member_output']['model'].objects.all(),
                'condition_member_output_group': member_config['condition_member_output_group']['model'].objects.all(),
            }

        elif self.type == 'conditionlinkgroup':
            member_type = 'conditionlinkmember'
            member_config = MEMBER_CONFIG[member_type]
            member_data = {
                'condition_link_member': member_config['condition_link_member']['model'].objects.all(),
                'condition_link_member_group': member_config['condition_link_member_group']['model'].objects.all(),
            }
            group_tbl = {'name': 'name', 'operator': 'operator', '': ''}

            if self.request.user_agent.is_mobile:
                member_tbl = {'order': '?order', 'type': '!pretty', 'name': 'name', 'description': 'description'}

            else:
                member_tbl = {'order': '?order', 'type': '!pretty', 'name': 'name'}

        elif self.type.endswith('group'):
            member_type = "%smember" % self.type.replace('group', '')
            member_config = MEMBER_CONFIG[member_type]
            member_data = {
                key: member_config[key]['model'].objects.all() for key in member_config.keys()
            }

        if self.type.startswith('output'):
            device_status = self._get_status(typ='outputobject')

        if member_type is not None:
            member_view_active, member_data_dict = member_pre_process(member_data_dict=member_data, request=self.request, member_config=member_config)
            tmpl = 'list/member'
            context = {
                'dataset': dataset, 'typ': self.type, 'request': self.request, 'member_data_dict': member_data_dict, 'MEMBER_CONFIG': member_config,
                'member_type': member_type, 'member_view_active': member_view_active, 'group_tbl': group_tbl, 'member_tbl': member_tbl, 'title': self.title,
                'MAIN_CONFIG': MAIN_CONFIG, 'device_status': device_status,
            }

        else:
            tmpl = 'list/default'
            context = {
                'dataset': dataset, 'typ': self.type, 'request': self.request, 'group_tbl': group_tbl, 'member_tbl': member_tbl, 'title': self.title,
                'MAIN_CONFIG': MAIN_CONFIG,
            }

        return tmpl, context

    def _get_detail(self):
        tmpl = 'detailed'

        try:
            data = self.model.objects.get(id=self.uid)
        except self.model.DoesNotExist:
            raise Pseudo404(ga={'request': self.request, 'msg': self.error_msgs['id']})

        data_dict = {}

        for attribute in data.field_list:
            form_widget = self.form.base_fields[attribute].widget
            if hasattr(form_widget, 'render_value'):
                value = CENSOR_STRING

            else:
                value = getattr(data, attribute)

            if attribute in LABEL_DICT:
                name = LABEL_DICT[attribute]

            else:
                name = attribute.capitalize()

            if attribute in HELP_DICT:
                info = HELP_DICT[attribute]

            else:
                info = '---'

            data_dict[name] = {'value': value, 'info': info}

        context = {'data': data, 'data_dict': data_dict, 'typ': self.type, 'title': self.title}

        return tmpl, context

    def _get_create(self):
        tmpl = 'change'
        form = self.form()

        if set_key(self.data, 'group') and set_key(self.data, 'member_type'):
            member_type = self.data['member_type']
            group_id = self.data['group']
            try:
                form = self.form({MEMBER_CONFIG[self.type][member_type]['group_key']: group_id})

            except KeyError:
                try:
                    if set_key(self.data, 'group_type'):
                        group_type = self.data['group_type']
                        form = self.form({MEMBER_CONFIG[group_type][member_type]['group_key']: group_id})

                except KeyError:
                    pass

        context = {'form': form, 'typ': self.type, 'title': self.title}
        return tmpl, context

    def _post_create(self):
        form = self.form(self.data)
        tmpl = f'{self.tmpl_root}/change.html'

        if form.is_valid():
            try:
                form.save()
                return redirect(self.post_redirect)

            except ValueError as error_msg:
                return render(self.request, tmpl, context={'form': form, 'typ': self.type, 'form_error': error_msg, 'title': self.title})

        else:
            return render(self.request, tmpl, context={'form': form, 'typ': self.type, 'title': self.title})

    def _get_update(self):
        try:
            existing_instance = get_object_or_404(self.model, id=self.uid)

        except Exception:
            raise Pseudo404(ga={'request': self.request, 'msg': self.error_msgs['id']})

        form = self.form(instance=existing_instance)

        tmpl = 'change'
        context = {'form': form, 'typ': self.type, 'title': self.title}

        return tmpl, context

    def _post_update(self):
        try:
            existing_instance = get_object_or_404(self.model, id=self.uid)

        except Exception:
            raise Pseudo404(ga={'request': self.request, 'msg': self.error_msgs['id']})

        form = self.form(self.data, instance=existing_instance)

        if form.is_valid():
            form.save()
            return redirect(self.post_redirect)

    def _post_delete(self):
        try:
            data = get_object_or_404(self.model, id=self.uid)

        except Exception:
            raise Pseudo404(ga={'request': self.request, 'msg': self.error_msgs['id']})

        data.delete()
        return redirect(self.post_redirect)

    def _get_status(self, typ: str) -> dict:
        status = {}

        for device in MAIN_CONFIG[typ]['model'].objects.all():
            result = api_sock(
                request=self.request,
                sock_data={
                    'type': typ,
                    'id': device.id,
                    'do': 'is_active',
                    'timeout': WEBUI_SOCKET_INFO_TIMEOUT,
                },
            )

            if result is None:
                # unknown
                status[device] = 99

            elif result is False:
                # idle
                status[device] = 0

            else:
                # active
                status[device] = 1

        return status

