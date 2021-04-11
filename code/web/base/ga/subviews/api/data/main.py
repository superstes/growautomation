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

# todo: summer time not working


@user_passes_test(authorized_to_read, login_url='/api/denied/')
def ApiData(request, input_device: int = None, period: str = None, period_data: int = None, start_ts: str = None, stop_ts: str = None, out_dict: bool = False):
    error = None

    if request.method == 'GET':
        if input_device is None:
            if 'input_device' not in request.GET:
                return handler400_api(msg='Need to specify input_device')

            input_device = int(request.GET['input_device'])

        input_device_obj = get_device_instance(input_device)
        data_unit = get_device_parent_setting(child_obj=input_device, setting='unit')
        data_type = get_device_parent_setting(child_obj=input_device, setting='datatype')

        _time = _get_time(request, _period=period, _period_data=period_data, _start_ts=start_ts, _stop_ts=stop_ts)

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

        data_dict = _prepare_data(request, data_list, data_type)

        if len(data_dict) > max_data_points:
            data_dict = _thin_out_data_points(data_dict, count=max_data_points)

        xy_data_list = []

        for time, data in data_dict.items():
            xy_data_list.append({'x': time, 'y': data})

        json_dict = {
            'device_id': int(input_device), 'device_name': input_device_obj.name, 'data_unit': data_unit, 'data_type': data_type, 'error': error,
            'xy_data': xy_data_list,
        }

        if out_dict:
            return json_dict

        else:
            return JsonResponse(data=json_dict)

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


def _prepare_data(request, data_list, data_type: str) -> dict:
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
        formatted_datetime = add_timezone(request, datetime_obj=data_obj.created)
        out_dict[datetime.strftime(formatted_datetime, DATETIME_TS_FORMAT)] = typ(data_obj.data)

    return out_dict


def _get_time(request, _period, _period_data, _start_ts, _stop_ts):
    start_ts = None
    stop_ts = None

    if 'start_ts' in request.GET:
        _start_ts = request.GET['start_ts']

    if 'stop_ts' in request.GET:
        _stop_ts = request.GET['stop_ts']

    if _start_ts is not None:
        start_ts = get_datetime_w_tz(request, dt_str=_start_ts)

        if _stop_ts is not None:
            stop_ts = get_datetime_w_tz(request, dt_str=_stop_ts)

        else:
            stop_ts = add_timezone(request, datetime_obj=datetime.now())

    if 'period' in request.GET and 'period_data' in request.GET:
        _period = request.GET['period']
        _period_data = int(request.GET['period_data'])

    if _period is not None and _period_data is not None:
        stop_ts = add_timezone(request, datetime_obj=datetime.now())

        if _period == 'y':
            start_ts = stop_ts - timedelta(days=(_period_data * 365))

        elif _period == 'm':
            start_ts = stop_ts - timedelta(days=(_period_data * 31))  # todo: should be exact

        elif _period == 'd':
            start_ts = stop_ts - timedelta(days=_period_data)

        elif _period == 'H':
            start_ts = stop_ts - timedelta(hours=_period_data)

        elif _period == 'M':
            start_ts = stop_ts - timedelta(minutes=_period_data)

        else:
            return handler400_api(msg='Unsupported time period type')

    if start_ts is None:
        return handler400_api(msg='No supported filter provided')

    else:

        return start_ts, stop_ts
