from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.db.utils import IntegrityError
from django.shortcuts import redirect

from core.utils.debug import web_log

from ...user import authorized_to_read, authorized_to_write
from ..handlers import Pseudo404
from ...config import shared as config
from ...utils.web import get_client_ip
from ...utils.auth import method_user_passes_test


TITLE = 'System users'


class UserMgmt:
    GA_GROUPS = {
        # config.GA_ADMIN_GROUP: {
        #     'privs': 'ADMIN',
        #     'pretty': 'ALL',
        # },
        config.GA_WRITE_GROUP: {
            'privs': 'WRITE',
            'pretty': 'READ+WRITE',
        },
        config.GA_READ_GROUP: {
            'privs': 'READ',
            'pretty': 'READ',
        },
    }

    def __init__(self, request):
        self.request = request

    @method_user_passes_test(authorized_to_read, login_url=config.DENIED_URL)
    def go(self):
        if self.request.method == 'GET':
            return self._list()

        else:
            action = self.request.POST['do']

            if action == 'create':
                return self._create()

            elif action == 'delete':
                return self._delete()

            elif action == 'update':
                return self._update()

            else:
                raise Pseudo404(ga={'request': self.request, 'msg': f"Got unsupported user action: '{action}'"})

    @method_user_passes_test(authorized_to_read, login_url=config.DENIED_URL)
    def _list(self, msg: str = None, msg_style: str = 'success'):
        users = User.objects.all().exclude(username=config.GA_ADMIN_USER)

        update_user = None
        create_user = False

        if 'do' in self.request.GET and self.request.GET['do'] == 'create':
            create_user = True

        for user in users:
            if 'do' in self.request.GET and self.request.GET['do'] == 'update' \
                    and 'name' in self.request.GET and self.request.GET['name'] == user.username:
                update_user = user.username
                break

        return render(self.request, 'system/users.html', context={
            'request': self.request, 'title': TITLE, 'users': users, 'GA_GROUPS': self.GA_GROUPS, 'action_msg': msg, 'action_msg_style': msg_style,
            'update_user': update_user, 'create_user': create_user,
        })

    @method_user_passes_test(authorized_to_write, login_url=config.DENIED_URL)
    def _create(self):
        try:
            user = User.objects.create_user(
                username=self.request.POST['name'],
                email=self.request.POST['email'],
                password=self.request.POST['password'],
            )

            privs = self.request.POST['privileges']
            user.groups.add(Group.objects.get(name=config.GA_USER_GROUP))

            for grp, value in self.GA_GROUPS.items():
                if privs.find(value['pretty']) != -1:
                    user.groups.add(Group.objects.get(name=grp))

            self._log_action(action='created')
            return self._list(msg=f"User '{self.request.POST['name']}' successfully created!")

        except IntegrityError:
            return self._list(msg=f"User '{self.request.POST['name']}' already exists!", msg_style='danger')

    @method_user_passes_test(authorized_to_write, login_url=config.DENIED_URL)
    def _update(self):
        user = User.objects.get(username=self.request.POST['current_name'])
        user.username = self.request.POST['name']
        user.email = self.request.POST['email']
        privs = self.request.POST['privileges']
        pwd = self.request.POST['password']

        if pwd != ' ' and pwd != config.CENSOR_STRING:
            user.set_password(pwd)

        user.groups.add(Group.objects.get(name=config.GA_USER_GROUP))

        try:
            for grp, value in self.GA_GROUPS.items():
                grp_obj = Group.objects.get(name=grp)
                if privs.find(value['pretty']) != -1:
                    user.groups.add(grp_obj)

                else:
                    user.groups.remove(grp_obj)

            self._log_action(action='updated')
            msg = f"User '{self.request.POST['name']}' successfully updated!"
            msg_style = 'success'

        except Exception as error:
            web_log(
                output=f"User '{self.request.POST['name']}' could not be added to a group! It could be that the group does not exist! Error: {error}",
                level=3
            )
            msg = f"User '{self.request.POST['name']}' could not be added to all groups!"
            msg_style = 'warning'

        user.save()

        if self.request.POST['name'] == str(self.request.user):
            return redirect(config.LOGOUT_URL)

        return self._list(msg=msg, msg_style=msg_style)

    @method_user_passes_test(authorized_to_write, login_url=config.DENIED_URL)
    def _delete(self):
        if self.request.POST['name'] == str(self.request.user):
            return self._list(msg='You cannot delete the user you are currently logged-in with!', msg_style='danger')

        if len(User.objects.all()) > 2:
            User.objects.get(username=self.request.POST['name']).delete()
            self._log_action(action='deleted', level=2)
            return self._list(msg=f"User '{self.request.POST['name']}' successfully deleted!")

        else:
            return self._list(msg=f"It seems only this user exists => you cannot delete this one!", msg_style='warning')

    def _log_action(self, action: str, level: int = 3):
        web_log(
            output=f"User '{self.request.POST['name']}' was {action} by user '{self.request.user}' from client ip '{get_client_ip(self.request)}'",
            level=level,
        )
