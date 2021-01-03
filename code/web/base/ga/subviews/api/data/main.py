from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime, timedelta
from itertools import islice
from math import ceil

from ....models import InputDataModel
from ...handlers import handler400_api
from ....utils.helper import get_device_parent_setting, add_timezone, get_device_instance, get_datetime_w_tz
from ....user import authorized_to_read
from ....config.shared import DATETIME_TS_FORMAT


MAX_DATA_POINTS_SHORT = 150
MAX_DATA_POINTS_MEDIUM = 500
MAX_DATA_POINTS_LONG = 1000


@user_passes_test(authorized_to_read, login_url='/api/denied/')
def ApiData(request):
    # time -> start/stop/last X min/h/d/m/y
    # every chart gets a maximum of X datapoints (because of performance etc)
    # chart.js settings
    #   array of unimportant chart.js settings
    #   form fields for important ones

    error = None

    if request.method == 'GET':
        if 'input_device' not in request.GET:
            return handler400_api(msg='Need to specify input_device')

        input_device = int(request.GET['input_device'])
        input_device_obj = get_device_instance(input_device)
        data_unit = get_device_parent_setting(child_obj=input_device, setting='unit')
        data_type = get_device_parent_setting(child_obj=input_device, setting='datatype')

        _time = _get_time(request)

        if type(_time) != tuple:
            return _time

        start_ts, stop_ts = _time

        time_span = stop_ts - start_ts
        if time_span > timedelta(days=30):
            max_data_points = MAX_DATA_POINTS_LONG

        elif time_span > timedelta(days=7):
            max_data_points = MAX_DATA_POINTS_MEDIUM

        else:
            max_data_points = MAX_DATA_POINTS_SHORT

        data_list = InputDataModel.objects.filter(
            created__gte=start_ts,
            created__lte=stop_ts,
            obj=input_device
        ).order_by('-created')

        data_dict = _prepare_data(data_list, data_type)

        if len(data_dict) > max_data_points:
            data_dict = _thin_out_data_points(data_dict, count=max_data_points)

        time_list, data_list = [], []

        for time, data in data_dict.items():
            time_list.append(time)
            data_list.append(data)

        return JsonResponse(data={
            'device_id': int(input_device), 'device_name': input_device_obj.name, 'data_unit': data_unit, 'data_type': data_type, 'time_list': time_list,
            'data_list': data_list, 'error': error,
        })

    else:
        return handler400_api(msg='Only GET method supported')


def _thin_out_data_points(data_dict: dict, count: int) -> dict:
    data_point_count = len(data_dict)

    interval = ceil(data_point_count / count)

    # if a dict will be needed again
    _winners = dict(islice(enumerate(data_dict), None, None, interval))

    out_dict = {}

    for _ in _winners.values():
        out_dict[_] = data_dict[_]

    # return data_list[0::interval]
    return out_dict


def _prepare_data(data_list, data_type: str) -> dict:
    out_dict = {}

    if data_type == 'float':
        typ = float
    elif data_type == 'int':
        typ = int
    elif data_type == 'bool':
        typ = bool
    else:
        typ = str

    for data_obj in data_list:
        out_dict[datetime.strftime(data_obj.created, DATETIME_TS_FORMAT)] = typ(data_obj.data)

    return out_dict


def _get_time(request):
    if 'start_ts' in request.GET:
        start_ts = get_datetime_w_tz(request, dt_str=request.GET['start_ts'])

        if 'stop_ts' in request.GET:
            stop_ts = get_datetime_w_tz(request, dt_str=request.GET['stop_ts'])

        else:
            stop_ts = add_timezone(request, datetime_obj=datetime.now())

    elif 'period' in request.GET and 'period_data' in request.GET:
        period = request.GET['period']
        period_data = int(request.GET['period_data'])

        stop_ts = add_timezone(request, datetime_obj=datetime.now())

        if period == 'y':
            start_ts = stop_ts - timedelta(days=(period_data * 365))

        elif period == 'm':
            start_ts = stop_ts - timedelta(days=(period_data * 31))  # todo: should be exact

        elif period == 'd':
            start_ts = stop_ts - timedelta(days=period_data)

        elif period == 'H':
            start_ts = stop_ts - timedelta(hours=period_data)

        elif period == 'M':
            start_ts = stop_ts - timedelta(minutes=period_data)

        else:
            return handler400_api(msg='Unsupported time period type')

    else:
        return handler400_api(msg='No supported filter provided')

    return start_ts, stop_ts
