from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime, timedelta
from time import sleep

from ...user import authorized_to_read, authorized_to_write
from ...utils.basic import get_time_difference
from ...utils.helper import develop_subprocess, develop_log, get_server_config
from ..handlers import Pseudo404
from ...config import shared as config

# need to allow www-data to start/stop/restart/reload services
SYSTEMCTL = '/bin/systemctl'
SHELL_SERVICE_STATUS = f"{SYSTEMCTL} is-active %s"
SHELL_SERVICE_ENABLED = f"{SYSTEMCTL} is-enabled %s"
SHELL_SERVICE_ACTIVE_TIMESTAMP = f"{SYSTEMCTL} show -p ActiveEnterTimestamp --value %s"
SHELL_SERVICE_INACTIVE_TIMESTAMP = f"{SYSTEMCTL} show -p InactiveEnterTimestamp --value %s"
TITLE = 'System service'


@user_passes_test(authorized_to_read, login_url=config.DENIED_URL)
def ServiceView(request):
    service_name_options = {
        'GrowAutomation': config.CORE_SERVICE,
        'Webserver': 'apache2.service',
        'Database': get_server_config(setting='sql_service'),
    }
    non_stop_services = ['Webserver', 'Database']
    if get_server_config(setting='letsencrypt'):
        service_name_options.update({'Certificate renewal': config.LE_RENEWAL_SERVICE})

    service_name = 'GrowAutomation'
    service_status = None
    service_runtime = None
    service_enabled = None
    reload_time = 60

    if 'reload_time' in request.GET:
        reload_time = request.GET['reload_time']

    # todo clean up and fix service time counter

    if 'service_name' in request.GET:
        service_name = request.GET['service_name']

    elif 'service_name' in request.POST:
        service_name = request.POST['service_name']

    service_value = service_name_options[service_name]

    # get status times
    if service_status == 'active':
        status_command = SHELL_SERVICE_ACTIVE_TIMESTAMP

    else:
        status_command = SHELL_SERVICE_INACTIVE_TIMESTAMP

    dev_time = str((datetime.now() - timedelta(minutes=5)).strftime(f'%a {config.DATETIME_TS_FORMAT}')) + ' GMT'
    service_status_time = develop_subprocess(request, command=status_command % service_value, develop=dev_time)

    if service_status_time not in config.NONE_RESULTS:
        service_runtime = get_time_difference(service_status_time.rsplit(' ', 1)[0], f'%a {config.DATETIME_TS_FORMAT}')

    if request.method == 'GET':
        if service_name not in service_name_options:
            raise Pseudo404(ga={'request': request, 'msg': f"Service \"{service_name}\" not manageable"})

        service_status = develop_subprocess(request, command=SHELL_SERVICE_STATUS % service_value, develop='active')
        service_enabled = develop_subprocess(request, command=SHELL_SERVICE_ENABLED % service_value, develop='enabled')

        if reload_time is None:
            reload_time = config.WEBUI_DEFAULT_REFRESH_SECS

    else:
        if 'service_name' in request.POST:
            if service_runtime is not None and service_runtime > config.WEBUI_SVC_ACTION_COOLDOWN and 'service_action' in request.POST:
                service_action(request=request, service=service_value)

            return redirect(f"/system/service/?service_name={service_name.replace(' ', '+')}")

    return render(request, 'system/service.html', context={
        'request': request, 'service_name': service_name, 'service_value': service_value, 'service_status': service_status,
        'service_name_options': service_name_options, 'service_status_time': service_status_time, 'service_enabled': service_enabled,
        'service_runtime': service_runtime, 'reload_time': reload_time, 'non_stop_services': non_stop_services, 'title': TITLE,
    })


@user_passes_test(authorized_to_write, login_url=config.DENIED_URL)
def service_action(request, service: str):
    action = request.POST['service_action']
    develop_log(request, f"{action}ing service {service}")

    if action in ['start', 'stop', 'reload', 'restart']:
        develop_log(
            request=request,
            output=f"{request.META['PATH_INFO']} - action \"{action} service {service}\" "
                   f"was executed by user {request.user} from remote ip {request.META['REMOTE_ADDR']}"
        )
        develop_subprocess(request=request, command=f"sudo {SYSTEMCTL} {action} {service}", develop='ok')
        sleep(1)

    else:
        develop_log(request=request, output=f"Got unsupported service action: '{action}'")
