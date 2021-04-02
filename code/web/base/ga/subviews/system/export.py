from django.shortcuts import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test

from datetime import datetime
from os import path as os_path

from ...user import authorized_to_write
from ...utils.helper import get_controller_setting, develop_subprocess
from ...subviews.handlers import Pseudo404


@user_passes_test(authorized_to_write, login_url='/denied/')
def export_view(request):
    dump_file = f"dump_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.sql.xz"
    dump_file_path = f'/tmp/{dump_file}'
    sql_config_file = f'{settings.BASE_DIR}/database.cnf'
    dump_db = get_controller_setting(request=request, setting='sql_database')

    exclude_tables = [
        '',
        'auth_group',
        'auth_group_permissions',
        'auth_permission',
        'auth_user',
        'auth_user_groups',
        'auth_user_user_permissions',
        'django_admin_log',
        'django_content_type',
        'django_migrations',
        'django_session',
        'ga_inputdatamodel',
        'ga_dashboardmodel',
        'ga_test',
    ]
    exclude_string = ' --ignore-table=ga.'.join(exclude_tables)
    dump_command = f"mysqldump --defaults-file={sql_config_file} {dump_db} --single-transaction {exclude_string} | xz -7 > {dump_file_path}"

    develop_subprocess(request, command=dump_command, develop='nope!')

    if os_path.exists(dump_file_path):
        with open(dump_file_path, 'rb') as dump:
            response = HttpResponse(dump.read(), content_type='application/x-xz')
            response['Content-Disposition'] = f'inline; filename={dump_file}'
            return response

    raise Pseudo404(ga={'request': request, 'msg': f'Could not dump database config!'})
