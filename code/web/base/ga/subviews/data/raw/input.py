from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone

from ....user import authorized_to_read
from ....models import InputDataModel, ObjectInputModel
from ....utils.basic import get_datetime_w_tz
from ....utils.helper import get_device_parent_setting
from ....config.shared import WEBUI_MAX_ENTRY_RANGE, WEBUI_DEFAULT_DATA_TABLE_ROWS, WEBUI_EMPTY_CHOICE

TITLE = 'Data table'


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
    result_count = WEBUI_DEFAULT_DATA_TABLE_ROWS

    if 'start_ts' in request.GET:
        start_ts = get_datetime_w_tz(request, dt_str=request.GET['start_ts'])

        if 'stop_ts' in request.GET:
            _stop_ts = get_datetime_w_tz(request, dt_str=request.GET['stop_ts'])

            if _stop_ts is not None:
                if _stop_ts > start_ts:
                    stop_ts = _stop_ts

                else:
                    stop_ts_ok = False

    if 'result_count' in request.GET and int(request.GET['result_count']) in WEBUI_MAX_ENTRY_RANGE:
        result_count = int(request.GET['result_count'])

    if 'input_device' in request.GET and request.GET['input_device'] != WEBUI_EMPTY_CHOICE:
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
        'request': request, 'start_ts': start_ts, 'stop_ts': stop_ts, 'input_device_dict': input_device_dict,
        'input_device': input_device, 'result_count': result_count, 'result_count_range': WEBUI_MAX_ENTRY_RANGE, 'data_list': data_list,
        'data_unit': data_unit, 'data_type': data_type, 'stop_ts_ok': stop_ts_ok, 'title': TITLE,
    })
