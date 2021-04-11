from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime
from os import listdir as os_listdir

from ...user import authorized_to_read
from ...utils.helper import check_develop, get_controller_setting, str_to_list, develop_subprocess

# need to add www-data to systemd-journal group (usermod -a -G systemd-journal www-data)

SHELL_MAX_LOG_LINES = 25
SHELL_MAX_LOG_LINES_RANGE = range(25, 1025, 25)
SHELL_SERVICE_STATUS = "/bin/systemctl show -p ActiveState --value %s"
SHELL_SERVICE_LOG_STATUS = "/bin/systemctl status %s -l --no-pager"
SHELL_SERVICE_LOG_JOURNAL = "/bin/journalctl -u %s --no-pager -n %s"
DEFAULT_REFRESH_SECS = 30
TITLE = 'System logs'


@user_passes_test(authorized_to_read, login_url='/denied/')
def LogView(request):
    develop = check_develop(request)
    date_year = datetime.now().strftime('%Y')
    date_month = datetime.now().strftime('%m')
    path_log = get_controller_setting(request, 'path_log')

    log_type_options = ['Service', 'Service journal', 'GrowAutomation']
    log_service_options = {
        'GrowAutomation': 'ga_core.service',
        'Apache webserver': 'apache2.service',
        'Mariadb database': 'mariadb.service',
        'LetsEncrypt renewal': 'ga_web_certRenewal.service',
    }

    if develop:
        device_log_list = ['02_device_test1.log', '02_device_earth_humidity.log', '']

    else:
        try:
            device_log_list = os_listdir("%s/device/%s/" % (path_log, date_year))

        except FileNotFoundError:
            device_log_list = []

    log_ga_options = {
        'Core': "%s/core/%s/%s_core.log" % (path_log, date_year, date_month),
        'Web': "%s/web/%s/%s_web.log" % (path_log, date_year, date_month),
    }

    for device_log in device_log_list:
        try:
            device = device_log.split('_', 2)[2].rsplit('.', 1)[0]
            log_ga_options["Device '%s'" % device] = "%s/device/%s/%s" % (path_log, date_year, device_log)

        except IndexError:
            log_ga_options["Log '%s'" % device_log] = "%s/device/%s/%s" % (path_log, date_year, device_log)

    if 'log_entry_count' in request.GET and \
            int(request.GET['log_entry_count']) in SHELL_MAX_LOG_LINES_RANGE:
        log_entry_count = int(request.GET['log_entry_count'])

    else:
        log_entry_count = SHELL_MAX_LOG_LINES

    log_file = None
    log_type = None
    log_data = None
    log_subtype = None
    log_subtype_options = None
    log_subtype_option_list = None
    reload_time = None

    if 'reload_time' in request.GET:
        reload_time = request.GET['reload_time']

    if 'log_type' in request.GET and request.GET['log_type'] in log_type_options:
        log_type = request.GET['log_type']

        if 'log_subtype' in request.GET and request.GET['log_subtype'] in log_service_options:
            log_subtype = request.GET['log_subtype']
            log_service_value = log_service_options[log_subtype]

            if log_type == 'Service':
                if develop:
                    log_data = ['test data', 'data service']

                else:
                    log_data = str_to_list(
                        develop_subprocess(
                            request,
                            command=SHELL_SERVICE_LOG_STATUS % log_service_value,
                            develop=['Test output1', 'Helloo', "Third time's a charm"]
                        )
                    )
            elif log_type == 'Service journal':
                if develop:
                    log_data = ['test data', 'data journal']

                else:
                    log_data = str_to_list(
                        develop_subprocess(
                            request,
                            command=SHELL_SERVICE_LOG_JOURNAL % (log_service_value, log_entry_count),
                            develop=['Test output2', 'Helloo', "Third time's a charm"]
                        )
                    )

        if log_type == 'GrowAutomation':
            log_subtype_options = log_ga_options

            if 'log_subtype' in request.GET and request.GET['log_subtype'] in log_ga_options:
                log_subtype = request.GET['log_subtype']
                log_file = log_ga_options[log_subtype]

                # option to view older (truncated) logs?
                if develop:
                    log_data = [f"log from file '{path_log}' -> test data", 'data ga']

                else:
                    log_data = str_to_list(
                        develop_subprocess(
                            request,
                            command=f"tail -n {log_entry_count} {log_file}",
                            develop=['Test output3', 'Helloo', "Third time's a charm"]
                        ),
                        reverse=True
                    )

        else:
            log_subtype_options = log_service_options

        if 'log_subtype' in request.GET:
            if reload_time is None:
                reload_time = DEFAULT_REFRESH_SECS

    if type(log_data) == list and len(log_data) == 0:
        log_data = None

    if log_subtype_options is not None:
        log_subtype_option_list = sorted([key for key in log_subtype_options.keys()])

    return render(request, 'system/log.html', context={
        'request': request, 'log_data': log_data, 'log_type_options': log_type_options, 'log_type': log_type,
        'log_subtype': log_subtype, 'log_entry_count': log_entry_count, 'log_entry_range': SHELL_MAX_LOG_LINES_RANGE, 'log_file': log_file,
        'log_subtype_option_list': log_subtype_option_list, 'reload_time': reload_time, 'title': TITLE,
    })
