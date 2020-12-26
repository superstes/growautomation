from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime, timedelta

from ...user import authorized_to_read, authorized_to_write
from ...config.nav import nav_dict
from ...utils.process import subprocess
from ...utils.helper import check_develop, get_time_difference

SHELL_SERVICE_STATUS = "/bin/systemctl show -p ActiveState --value %s"
SHELL_SERVICE_STATUS_TIMESTAMP = "/bin/systemctl show -p ActiveEnterTimestamp --value %s"

# need to allow www-data to start/stop/restart/reload services


def custom_subprocess(command, develop: str = None) -> str:
    if check_develop():
        return develop

    return subprocess(command)


@user_passes_test(authorized_to_read, login_url='/denied/')
def ServiceView(request):
    service_name_options = {
        'Growautomation': 'ga.service',
        'Apache webserver': 'apache2.service'
    }

    service_status = None
    service_name = None
    service_value = None
    service_runtime = None
    service_runtime_clean = None
    service_status_time = None

    # todo clean up and fix service time counter

    if 'service_name' in request.GET:
        dev_time = str((datetime.now() - timedelta(minutes=5)).strftime('%a %Y-%m-%d %H:%M:%S')) + ' GMT'
        service_status_time = custom_subprocess(SHELL_SERVICE_STATUS_TIMESTAMP % service_value, dev_time)

        if service_status_time is not None and service_status_time != '':
            service_runtime = get_time_difference(service_status_time.rsplit(' ', 1)[0], '%a %Y-%m-%d %H:%M:%S')

            if service_runtime is not None:
                service_runtime_clean = str(timedelta(seconds=service_runtime))

    if request.method == 'POST':
        if 'service_name' in request.POST and request.POST['service_name'] in service_name_options:
            service_name = request.POST['service_name']
            service_value = service_name_options[service_name]

            if service_runtime is not None and service_runtime > 60:
                service_action(request, service=service_value)
            else:
                return redirect("/system/service/?service_name=%s" % service_name.replace(' ', '+'))

            service_status = custom_subprocess(SHELL_SERVICE_STATUS % service_value, 'active')
            service_status_time = custom_subprocess(SHELL_SERVICE_STATUS_TIMESTAMP % service_value, dev_time)

    else:
        if 'service_name' in request.GET and request.GET['service_name'] in service_name_options:
            service_name = request.GET['service_name']
            service_value = service_name_options[service_name]

            service_status = custom_subprocess(SHELL_SERVICE_STATUS % service_value, 'active')

    return render(request, 'system/service.html', context={
        'request': request, 'nav_dict': nav_dict, 'service_name': service_name, 'service_value': service_value, 'service_status': service_status,
        'service_name_options': service_name_options, 'service_status_time': service_status_time,
        'service_runtime': service_runtime_clean,
    })


@user_passes_test(authorized_to_write, login_url='/denied/')
def service_action(request, service: str):
    # todo: log commands
    systemctl = 'sudo systemctl'
    if 'service_start' in request.POST:
        subprocess("%s start %s" % (systemctl, service))

    elif 'service_reload' in request.POST:
        subprocess("%s reload %s" % (systemctl, service))

    elif 'service_restart' in request.POST:
        subprocess("%s restart %s" % (systemctl, service))

    elif 'service_stop' in request.POST:
        subprocess("%s stop %s" % (systemctl, service))
