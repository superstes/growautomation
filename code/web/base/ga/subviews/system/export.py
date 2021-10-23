from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import user_passes_test

from datetime import datetime
from os import path as os_path

from ...user import authorized_to_write
from ...utils.helper import get_server_config, develop_subprocess
from ...subviews.handlers import Pseudo404
from ...config import shared as config


@user_passes_test(authorized_to_write, login_url=config.DENIED_URL)
def export_view(request, process: str):
    dump_file = f"dump_{process}_{datetime.now().strftime(config.DATETIME_TS_FORMAT.replace(' ', '_').replace(':', '-'))}.sql.xz"
    dump_file_path = f'/tmp/{dump_file}'
    dump_db = get_server_config(request=request, setting='sql_database')
    include_tables = []
    exclude_tables = []

    if process == 'config':
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
            'ga_devicelogoutput',
            'ga_devicestateoutput',
        ]

    elif process == 'data':
        include_tables = [
            'ga_inputdatamodel',
            'ga_devicelogoutput',
        ]

    elif process == 'full':
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
            'ga_test',
        ]

    else:
        raise Pseudo404(ga={'request': request, 'msg': f"Unsupported export type '{process}'!"})

    develop_subprocess(
        request,
        command=f"mysqldump --defaults-file={config.SQL_CONFIG_FILE} {dump_db} --single-transaction "
                f"{' '.join(include_tables)}"
                f"{' --ignore-table=ga.'.join(exclude_tables)} | "
                f"xz -7 > {dump_file_path}",
        develop='Skipping dump in development environment!'
    )

    if os_path.exists(dump_file_path):
        with open(dump_file_path, 'rb') as dump:
            response = HttpResponse(dump.read(), content_type='application/x-xz')
            response['Content-Disposition'] = f'inline; filename={dump_file}'
            return response

    raise Pseudo404(ga={'request': request, 'msg': f'Could not dump database {process}!'})
