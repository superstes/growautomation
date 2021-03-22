from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime, timedelta
from time import sleep

from core.utils.debug import Log

from ...user import authorized_to_read, authorized_to_write
from ...utils.helper import get_time_difference, develop_subprocess, get_controller_obj
from ..handlers import handler404

logger = Log(typ='web', web_ctrl_obj=get_controller_obj())

# need to allow www-data to start/stop/restart/reload services

SHELL_SERVICE_STATUS = "/bin/systemctl is-active %s"
SHELL_SERVICE_ENABLED = "/bin/systemctl is-enabled %s"
SHELL_SERVICE_ACTIVE_TIMESTAMP = "/bin/systemctl show -p ActiveEnterTimestamp --value %s"
SHELL_SERVICE_INACTIVE_TIMESTAMP = "/bin/systemctl show -p InactiveEnterTimestamp --value %s"
DEFAULT_REFRESH_SECS = 120


@user_passes_test(authorized_to_read, login_url='/denied/')
def ServiceView(request):
    service_name_options = {
        'Growautomation': 'ga.service',
        'Apache webserver': 'apache2.service',
        'Mariadb database': 'mariadb.service',
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
            return handler404(request, msg="Service '%s' not manageable" % service_name)

        service_value = service_name_options[service_name]

        service_status = develop_subprocess(request, command=SHELL_SERVICE_STATUS % service_value, develop='active')
        service_enabled = develop_subprocess(request, command=SHELL_SERVICE_ENABLED % service_value, develop='enabled')

        if service_status == 'active':
            status_command = SHELL_SERVICE_ACTIVE_TIMESTAMP
        else:
            status_command = SHELL_SERVICE_INACTIVE_TIMESTAMP

        dev_time = str((datetime.now() - timedelta(minutes=5)).strftime('%a %Y-%m-%d %H:%M:%S')) + ' GMT'
        service_status_time = develop_subprocess(request, command=status_command % service_value, develop=dev_time)

        if service_status_time is not None and service_status_time != '':
            service_runtime = get_time_difference(service_status_time.rsplit(' ', 1)[0], '%a %Y-%m-%d %H:%M:%S')

        if reload_time is None:
            reload_time = DEFAULT_REFRESH_SECS

    if request.method == 'POST':
        if 'service_name' in request.POST:
            if service_runtime is not None and service_runtime > 60:
                service_action(request, service=service_value)
                sleep(1)

            return redirect("/system/service/?service_name=%s" % service_name.replace(' ', '+'))

    return render(request, 'system/service.html', context={
        'request': request, 'service_name': service_name, 'service_value': service_value, 'service_status': service_status,
        'service_name_options': service_name_options, 'service_status_time': service_status_time, 'service_enabled': service_enabled,
        'service_runtime': service_runtime, 'reload_time': reload_time, 'non_stop_services': non_stop_services,
    })


@user_passes_test(authorized_to_write, login_url='/denied/')
def service_action(request, service: str):
    systemctl = 'sudo /bin/systemctl'
    meta = request.META
    log_tmpl = f"{meta['PATH_INFO']} - action \"%s service {service}\" was executed by user {request.user} from remote ip {meta['REMOTE_ADDR']}"

    if 'service_start' in request.POST:
        logger.write(log_tmpl % 'start')
        develop_subprocess(request, command="%s start %s" % (systemctl, service), develop='ok')

    elif 'service_reload' in request.POST:
        logger.write(log_tmpl % 'reload')
        develop_subprocess(request, command="%s reload %s" % (systemctl, service), develop='ok')

    elif 'service_restart' in request.POST:
        logger.write(log_tmpl % 'restart')
        develop_subprocess(request, command="%s restart %s" % (systemctl, service), develop='ok')

    elif 'service_stop' in request.POST:
        logger.write(log_tmpl % 'stop')
        develop_subprocess(request, command="%s stop %s" % (systemctl, service), develop='ok')
