from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime

from ....user import authorized_to_read
from ....config.nav import nav_dict
from ....models import ObjectInputModel
from ....utils.helper import add_timezone
from ....config.shared import DATETIME_TS_FORMAT


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataChartView(request):

    return render(request, 'data/chart/dashboard.html', context={
        'request': request, 'nav_dict': nav_dict,
    })


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataChartCreateView(request):
    input_device_dict = {instance.name: instance.id for instance in ObjectInputModel.objects.all()}

    stop_ts = None
    start_ts = None
    input_device = None

    if 'input_device' in request.GET:
        input_device = int(request.GET['input_device'])

    if 'start_ts' in request.GET:
        _ = request.GET['start_ts']
        if _ not in [None, '']:
            start_ts_wo_tz = datetime.strptime(_, DATETIME_TS_FORMAT)
            start_ts = add_timezone(request, datetime_obj=start_ts_wo_tz)

        if 'stop_ts' in request.GET:
            _ = request.GET['stop_ts']
            if _ not in [None, '']:
                stop_ts_wo_tz = datetime.strptime(_, DATETIME_TS_FORMAT)
                _stop_ts = add_timezone(request, datetime_obj=stop_ts_wo_tz)

                if _stop_ts > start_ts:
                    stop_ts = _stop_ts

    return render(request, 'data/chart/create.html', context={
        'request': request, 'nav_dict': nav_dict, 'input_device_dict': input_device_dict, 'start_ts': start_ts, 'stop_ts': stop_ts, 'input_device': input_device,
    })
