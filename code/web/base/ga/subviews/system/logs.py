from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime

from ...user import authorized_to_read
from ...config.nav import nav_dict
from ...utils.process import subprocess
from ...utils.helper import check_develop
from ..handlers import handler404

SHELL_MAX_LOG_LINES = 100
SHELL_MAX_LOG_LINES_RANGE = range(25, 1025, 25)

SHELL_SERVICE_STATUS = "/bin/systemctl show -p ActiveState --value %s"
SHELL_SERVICE_LOG_STATUS = "/bin/systemctl status %s -l --no-pager"

# need to add www-data to systemd-journal group (usermod -a -G systemd-journal www-data)

SHELL_SERVICE_LOG_JOURNAL = "/bin/journalctl -u %s --no-pager -n %s"


@user_passes_test(authorized_to_read, login_url='/denied/')
def LogView(request):
    log_type_options = ['Service', 'Service journal', 'Growautomation']
    log_service_options = {
        'Growautomation': 'ga.service',
        'Apache webserver': 'apache2.service'
    }

    if 'log_entry_count' in request.GET and \
            int(request.GET['log_entry_count']) in SHELL_MAX_LOG_LINES_RANGE:
        log_entry_count = int(request.GET['log_entry_count'])
    else:
        log_entry_count = SHELL_MAX_LOG_LINES

    log_data = None
    log_type = None
    log_service = None
    develop = check_develop()

    if 'log_type' in request.GET and request.GET['log_type'] in log_type_options:
        log_type = request.GET['log_type']

        if 'log_service' in request.GET and request.GET['log_service'] in log_service_options:
            log_service = request.GET['log_service']
            log_service_value = log_service_options[log_service]

            if log_type == 'Service':
                if develop:
                    log_data = 'test data\ndata service'
                else:
                    log_data = subprocess(SHELL_SERVICE_LOG_STATUS % log_service_value)
            elif log_type == 'Service journal':
                if develop:
                    log_data = 'test data\ndata journal'
                else:
                    log_data = subprocess(SHELL_SERVICE_LOG_JOURNAL % (log_service_value, log_entry_count))

        if log_type == 'Growautomation':
            date_year = datetime.now().strftime('%Y')
            date_month = datetime.now().strftime('%m')
            # ObjectControllerModel.objects.all()
            # must get path to logfile
            # option to view older (truncated) logs?
            if develop:
                log_data = 'test data\ndata ga'
            else:
                log_data = subprocess("tail -n %s /var/log/growautomation/demo/%s/%s_core.log" % (log_entry_count, date_year, date_month))

    # try:
    #     filter_dict = get_filter_dict(model_obj.filter_dict, dataset)
    #     dataset, active_filter = apply_filter(request=request, dataset=dataset)
    # except AttributeError as error_msg:
    #     active_filter = None
    #
    #     if str(error_msg).find("has no attribute 'filter_dict'") != -1:
    #         filter_dict = {}
    #     else:
    #         filter_dict = error_msg

    if type(log_data) == str:
        log_data = log_data.split('\n')

    handler404(request=request, msg='test')

    return render(request, 'system/log.html', context={
        'request': request, 'nav_dict': nav_dict, 'log_data': log_data, 'log_type_options': log_type_options, 'log_service_options': log_service_options,
        'log_type': log_type, 'log_service': log_service, 'log_entry_count': log_entry_count, 'log_entry_range': SHELL_MAX_LOG_LINES_RANGE,
    })

