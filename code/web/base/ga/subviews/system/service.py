from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime, timedelta
from time import sleep

from ...user import authorized_to_read, authorized_to_write
from ...utils.basic import get_time_difference
from ...utils.helper import develop_subprocess, develop_log
from ..handlers import Pseudo404
from ...config import shared as config

# need to allow www-data to start/stop/restart/reload services
SHELL_SERVICE_STATUS = "/bin/systemctl is-active %s"
SHELL_SERVICE_ENABLED = "/bin/systemctl is-enabled %s"
SHELL_SERVICE_ACTIVE_TIMESTAMP = "/bin/systemctl show -p ActiveEnterTimestamp --value %s"
SHELL_SERVICE_INACTIVE_TIMESTAMP = "/bin/systemctl show -p InactiveEnterTimestamp --value %s"
TITLE = 'System service'


@user_passes_test(authorized_to_read, login_url='/denied/')
def ServiceView(request):
    service_name_options = {
        'GrowAutomation': 'ga_core.service',
        'Apache webserver': 'apache2.service',
        'Mariadb database': 'mariadb.service',
        'LetsEncrypt renewal': 'ga_web_certRenewal.timer',
    }
    non_stop_services = ['Apache webserver', 'Mariadb database']

    service_status = None
    service_name = None
    service_value = None
    service_runtime = None
    service_status_time = None
    service_enabled = None
    reload_time = None

    if 'reload_time' in request.GET:
        reload_time = request.GET['reload_time']

    # todo clean up and fix service time counter

    if 'service_name' in request.GET or 'service_name' in request.POST:
        if 'service_name' in request.GET:
            service_name = request.GET['service_name']

        else:
            service_name = request.POST['service_name']

        if service_name not in service_name_options:
            raise Pseudo404(ga={'request': request, 'msg': f"Service \"{service_name}\" not manageable"})

        service_value = service_name_options[service_name]

        service_status = develop_subprocess(request, command=SHELL_SERVICE_STATUS % service_value, develop='active')
        service_enabled = develop_subprocess(request, command=SHELL_SERVICE_ENABLED % service_value, develop='enabled')

        if service_status == 'active':
            status_command = SHELL_SERVICE_ACTIVE_TIMESTAMP

        else:
            status_command = SHELL_SERVICE_INACTIVE_TIMESTAMP

        dev_time = str((datetime.now() - timedelta(minutes=5)).strftime(f'%a {config.DATETIME_TS_FORMAT}')) + ' GMT'
        service_status_time = develop_subprocess(request, command=status_command % service_value, develop=dev_time)

        if service_status_time is not None and service_status_time != '':
            service_runtime = get_time_difference(service_status_time.rsplit(' ', 1)[0], f'%a {config.DATETIME_TS_FORMAT}')

        if reload_time is None:
            reload_time = config.WEBUI_DEFAULT_REFRESH_SECS

    if request.method == 'POST':
        if 'service_name' in request.POST:
            if service_runtime is not None and service_runtime > config.WEBUI_SVC_ACTION_COOLDOWN:
                service_action(request, service=service_value)
                sleep(1)

            return redirect(f"/system/service/?service_name={service_name.replace(' ', '+')}")

    return render(request, 'system/service.html', context={
        'request': request, 'service_name': service_name, 'service_value': service_value, 'service_status': service_status,
        'service_name_options': service_name_options, 'service_status_time': service_status_time, 'service_enabled': service_enabled,
        'service_runtime': service_runtime, 'reload_time': reload_time, 'non_stop_services': non_stop_services, 'title': TITLE,
    })


@user_passes_test(authorized_to_write, login_url='/denied/')
def service_action(request, service: str):
    systemctl = 'sudo /bin/systemctl'
    meta = request.META
    log_tmpl = f"{meta['PATH_INFO']} - action \"%s service {service}\" was executed by user {request.user} from remote ip {meta['REMOTE_ADDR']}"

    if 'service_start' in request.POST:
        develop_log(request=request, output=log_tmpl % 'start')
        develop_subprocess(request, command=f"{systemctl} start {service}", develop='ok')

    elif 'service_reload' in request.POST:
        develop_log(request=request, output=log_tmpl % 'reload')
        develop_subprocess(request, command=f"{systemctl} reload {service}", develop='ok')

    elif 'service_restart' in request.POST:
        develop_log(request=request, output=log_tmpl % 'restart')
        develop_subprocess(request, command=f"{systemctl} restart {service}", develop='ok')

    elif 'service_stop' in request.POST:
        develop_log(request=request, output=log_tmpl % 'stop')
        develop_subprocess(request, command=f"{systemctl} stop {service}", develop='ok')
