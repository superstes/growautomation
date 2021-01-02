from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime

from ....user import authorized_to_read
from ....config.nav import nav_dict
from ....config.shared import DATETIME_TS_FORMAT
from ....models import InputDataModel, ObjectInputModel, GroupInputModel


DATA_MAX_ENTRIES = 100
DATA_MAX_ENTRY_RANGE = range(25, 1025, 25)


@user_passes_test(authorized_to_read, login_url='/denied/')
def DataRawInputView(request):
    start_ts = None
    stop_ts = None
    input_device = None
    data_list = None
    data_unit = None
    data_type = None

    input_device_dict = {instance.name: instance.id for instance in ObjectInputModel.objects.all()}
    result_count = 100

    if 'start_ts' in request.GET:
        _ = request.GET['start_ts']
        if _ not in [None, '']:
            start_ts = datetime.strptime(_, DATETIME_TS_FORMAT)

        if 'stop_ts' in request.GET:
            _ = request.GET['stop_ts']
            if _ not in [None, '']:
                _2 = datetime.strptime(_, DATETIME_TS_FORMAT)

                if _2 > start_ts:
                    stop_ts = _2

    if 'result_count' in request.GET and int(request.GET['result_count']) in DATA_MAX_ENTRY_RANGE:
        result_count = int(request.GET['result_count'])

    if 'input_device' in request.GET:
        input_device = int(request.GET['input_device'])
        # data_unit = ObjectInputModel.objects.filter(name=input_device)
        # todo: get unit from input group -> will go from object over members to group

        if start_ts is None and stop_ts is None:
            data_list = InputDataModel.objects.filter(obj=input_device).order_by('created')[:result_count]

        elif start_ts is not None and stop_ts is None:
            data_list = InputDataModel.objects.filter(created__range=[start_ts, datetime.now()], obj=input_device).order_by('created')[:result_count]

        else:
            data_list = InputDataModel.objects.filter(created__range=[start_ts, stop_ts], obj=input_device).order_by('created')[:result_count]

    return render(request, 'data/raw/input.html', context={
        'request': request, 'nav_dict': nav_dict, 'start_ts': start_ts, 'stop_ts': stop_ts, 'input_device_dict': input_device_dict,
        'input_device': input_device, 'result_count': result_count, 'result_count_range': DATA_MAX_ENTRY_RANGE, 'data_list': data_list,
        'data_unit': data_unit, 'data_type': data_type,
    })
