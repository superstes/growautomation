from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime
from os import listdir as os_listdir
from os import path as os_path

from ...user import authorized_to_read
from ...utils.basic import str_to_list
from ...utils.helper import get_server_config, web_subprocess, read_last_lines
from ...config import shared as config

# need to add www-data to systemd-journal group (usermod -a -G systemd-journal www-data)
TITLE = 'System logs'


@user_passes_test(authorized_to_read, login_url=config.DENIED_URL)
def LogView(request):
    date_year = datetime.now().strftime('%Y')
    date_month = datetime.now().strftime('%m')
    path_log = get_server_config(setting='path_log')

    log_type_options = ['Service', 'Service journal', 'GrowAutomation']
    log_service_options = {
        'GrowAutomation': config.CORE_SERVICE,
        'Webserver': 'apache2.service',
        'Database': get_server_config(setting='sql_service'),
        'GrowAutomation Update': config.UPDATE_SERVICE,
    }

    if get_server_config(setting='letsencrypt'):
        log_service_options.update({'Certificate renewal': config.LE_RENEWAL_SERVICE})

    if 'log_entry_count' in request.GET and \
            int(request.GET['log_entry_count']) in config.WEBUI_MAX_ENTRY_RANGE:
        log_entry_count = int(request.GET['log_entry_count'])

    else:
        log_entry_count = config.WEBUI_LOG_MAX_LOG_LINES

    log_type = 'GrowAutomation'
    log_subtype = 'Core'
    log_file = None
    log_data = None
    log_subtype_options = log_service_options
    log_subtype_option_list = None
    reload_time = 60
    log_years = []
    log_months = []

    if 'reload_time' in request.GET:
        reload_time = request.GET['reload_time']

    if 'log_type' in request.GET and request.GET['log_type'] in log_type_options:
        log_type = request.GET['log_type']

    if log_type in ['Service', 'Service journal']:
        if 'log_subtype' in request.GET and request.GET['log_subtype'] in log_service_options:
            log_subtype = request.GET['log_subtype']

    if log_type == 'Service':
        try:
            log_service_value = log_service_options[log_subtype]

        except KeyError:
            log_service_value = log_service_options['GrowAutomation']

        log_data = str_to_list(
            web_subprocess(command=config.LOG_SERVICE_LOG_STATUS % log_service_value, log_stdout=False)
        )

    elif log_type == 'Service journal':
        try:
            log_service_value = log_service_options[log_subtype]

        except KeyError:
            log_service_value = log_service_options['GrowAutomation']

        log_data = str_to_list(
            web_subprocess(command=config.LOG_SERVICE_LOG_JOURNAL % (log_service_value, log_entry_count), log_stdout=False)
        )

    elif log_type == 'GrowAutomation':
        for item in os_listdir(f"{path_log}/core"):
            if os_path.isdir(f"{path_log}/core/{item}"):
                log_years.append(item)

        if 'log_year' in request.GET and request.GET['log_year'] in log_years:
            date_year = request.GET['log_year']

        for item in os_listdir(f"{path_log}/core/{date_year}"):
            log_months.append(item.split('_', 1)[0])

        log_months.sort()

        if 'log_month' in request.GET and request.GET['log_month'] in log_months:
            date_month = request.GET['log_month']

        try:
            device_log_list = os_listdir(f"{path_log}/device/{date_year}/")

        except FileNotFoundError:
            device_log_list = []

        log_ga_options = {
            'Core': f"{path_log}/core/{date_year}/{date_month}_core.log",
            'Web': f"{path_log}/web/{date_year}/{date_month}_web.log",
        }

        for device_log in device_log_list:
            try:
                device = device_log.split('_', 2)[2].rsplit('.', 1)[0]
                log_ga_options[f"Device '{device}'"] = f"{path_log}/device/{date_year}/{device_log}"

            except IndexError:
                log_ga_options[f"Log '{device_log}'"] = f"{path_log}/device/{date_year}/{device_log}"

        log_subtype_options = log_ga_options

        if 'log_subtype' in request.GET and request.GET['log_subtype'] in log_ga_options:
            log_subtype = request.GET['log_subtype']

        try:
            log_file = log_ga_options[log_subtype]

        except KeyError:
            log_file = log_ga_options['Core']

        # todo: option to view older (truncated) logs?
        log_data = read_last_lines(file=log_file, n=log_entry_count)

    else:
        log_subtype_options = log_service_options

    if 'log_subtype' in request.GET:
        if reload_time is None:
            reload_time = config.WEBUI_DEFAULT_REFRESH_SECS

    if type(log_data) == list and len(log_data) == 0:
        log_data = None

    if log_subtype_options is not None:
        log_subtype_option_list = sorted([key for key in log_subtype_options.keys()])

    return render(request, 'system/log.html', context={
        'request': request, 'log_data': log_data, 'log_type_options': log_type_options, 'log_type': log_type, 'log_years': log_years, 'log_months': log_months,
        'log_subtype': log_subtype, 'log_entry_count': log_entry_count, 'log_entry_range': config.WEBUI_MAX_ENTRY_RANGE, 'log_file': log_file,
        'log_subtype_option_list': log_subtype_option_list, 'reload_time': reload_time, 'title': TITLE, 'date_year': date_year, 'date_month': date_month,
    })
