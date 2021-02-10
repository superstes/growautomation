from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime
from os import listdir as os_listdir

from ...user import authorized_to_read
from ...config.nav import nav_dict
from ...utils.process import subprocess
from ...utils.helper import check_develop, get_controller_setting, add_line_numbers
from ..handlers import handler404

SHELL_MAX_LOG_LINES = 100
SHELL_MAX_LOG_LINES_RANGE = range(25, 1025, 25)

SHELL_SERVICE_STATUS = "/bin/systemctl show -p ActiveState --value %s"
SHELL_SERVICE_LOG_STATUS = "/bin/systemctl status %s -l --no-pager"

# need to add www-data to systemd-journal group (usermod -a -G systemd-journal www-data)

SHELL_SERVICE_LOG_JOURNAL = "/bin/journalctl -u %s --no-pager -n %s"


@user_passes_test(authorized_to_read, login_url='/denied/')
def LogView(request):
    # todo: if refresh is true
    #   window.setTimeout(function () {
    #     location.href = "$SAME_PAGE";
    #   }, $TIME_IN_MS);

    develop = check_develop(request)
    date_year = datetime.now().strftime('%Y')
    date_month = datetime.now().strftime('%m')
    path_log = get_controller_setting(request, 'path_log')

    log_type_options = ['Service', 'Service journal', 'Growautomation']
    log_service_options = {
        'Growautomation': 'ga.service',
        'Apache webserver': 'apache2.service'
    }

    if develop:
        device_log_list = ['02_device_test1.log', '02_device_earth_humidity.log', '']
    else:
        device_log_list = os_listdir("%s/device/%s/" % (path_log, date_year))

    log_ga_options = {
        'Core': "%s/core/%s/%s_core.log" % (path_log, date_year, date_month),
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

    if 'log_type' in request.GET and request.GET['log_type'] in log_type_options:
        log_type = request.GET['log_type']

        if 'log_subtype' in request.GET and request.GET['log_subtype'] in log_service_options:
            log_subtype = request.GET['log_subtype']
            log_service_value = log_service_options[log_subtype]

            if log_type == 'Service':
                if develop:
                    log_data = 'test data\ndata service'
                else:
                    log_data = add_line_numbers(subprocess(SHELL_SERVICE_LOG_STATUS % log_service_value))
            elif log_type == 'Service journal':
                if develop:
                    log_data = 'test data\ndata journal'
                else:
                    log_data = add_line_numbers(subprocess(SHELL_SERVICE_LOG_JOURNAL % (log_service_value, log_entry_count)))

        if log_type == 'Growautomation':
            log_subtype_options = log_ga_options

            if 'log_subtype' in request.GET and request.GET['log_subtype'] in log_ga_options:
                log_subtype = request.GET['log_subtype']
                log_file = log_ga_options[log_subtype]

                # option to view older (truncated) logs?
                if develop:
                    log_data = "log from file '%s' -> test data\ndata ga" % path_log
                else:
                    log_data = add_line_numbers(subprocess("tail -n %s %s" % (log_entry_count, log_file)), reverse=True)

        else:
            log_subtype_options = log_service_options

    if type(log_data) == str and len(log_data) == 0:
        log_data = None

    handler404(request=request, msg='test')

    if log_subtype_options is not None:
        log_subtype_option_list = sorted([key for key in log_subtype_options.keys()])

    return render(request, 'system/log.html', context={
        'request': request, 'nav_dict': nav_dict, 'log_data': log_data, 'log_type_options': log_type_options, 'log_type': log_type,
        'log_subtype': log_subtype, 'log_entry_count': log_entry_count, 'log_entry_range': SHELL_MAX_LOG_LINES_RANGE, 'log_file': log_file,
        'log_subtype_option_list': log_subtype_option_list
    })

