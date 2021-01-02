from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from datetime import datetime

from ....user import authorized_to_read
from ....config.nav import nav_dict
from ....config.shared import DATETIME_TS_FORMAT
from ....models import InputDataModel, ObjectInputModel
from ....utils.helper import add_timezone, get_device_parent_setting


DATA_MAX_ENTRY_RANGE = range(25, 1025, 25)


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataListView(request):
    start_ts = None
    stop_ts = None
    input_device = None
    data_list = None
    data_unit = None
    data_type = None
    stop_ts_ok = None

    input_device_dict = {instance.name: instance.id for instance in ObjectInputModel.objects.all()}
    result_count = 100

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

                else:
                    stop_ts_ok = False

    if 'result_count' in request.GET and int(request.GET['result_count']) in DATA_MAX_ENTRY_RANGE:
        result_count = int(request.GET['result_count'])

    if 'input_device' in request.GET:
        input_device = int(request.GET['input_device'])
        data_unit = get_device_parent_setting(child_obj=input_device, setting='unit')
        data_type = get_device_parent_setting(child_obj=input_device, setting='datatype')

        if start_ts is None and stop_ts is None:
            data_list = InputDataModel.objects.filter(
                obj=input_device
            ).order_by('-created')[:result_count]

        elif start_ts is not None and stop_ts is None:
            data_list = InputDataModel.objects.filter(
                created__gte=start_ts,
                created__lte=timezone.now(),
                obj=input_device
            ).order_by('-created')[:result_count]

        else:
            data_list = InputDataModel.objects.filter(
                created__gte=start_ts,
                created__lte=stop_ts,
                obj=input_device
            ).order_by('-created')[:result_count]

    return render(request, 'data/raw/input.html', context={
        'request': request, 'nav_dict': nav_dict, 'start_ts': start_ts, 'stop_ts': stop_ts, 'input_device_dict': input_device_dict,
        'input_device': input_device, 'result_count': result_count, 'result_count_range': DATA_MAX_ENTRY_RANGE, 'data_list': data_list,
        'data_unit': data_unit, 'data_type': data_type, 'stop_ts_ok': stop_ts_ok,
    })
