from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime, timedelta
from itertools import islice
from math import ceil

from ....models import InputDataModel
from ...handlers import handler404_api
from ....utils.helper import get_device_parent_setting, add_timezone
from ....user import authorized_to_read
from ....config.shared import DATETIME_TS_FORMAT


MAX_DATA_POINTS = 500


@user_passes_test(authorized_to_read, login_url='/api/denied/')
def ApiData(request):
    # time -> start/stop/last X min/h/d/m/y
    # every chart gets a maximum of X datapoints (because of performance etc)
    # chart.js settings
    #   array of unimportant chart.js settings
    #   form fields for important ones

    if request.method == 'GET':
        if 'input_device' not in request.GET:
            return handler404_api(msg='Need to specify input_device')

        input_device = int(request.GET['input_device'])
        data_unit = get_device_parent_setting(child_obj=input_device, setting='unit')
        data_type = get_device_parent_setting(child_obj=input_device, setting='datatype')

        _time = _get_time(request)

        if type(_time) != tuple:
            return _time

        start_ts, stop_ts = _time

        data_list = InputDataModel.objects.filter(
            created__gte=start_ts,
            created__lte=stop_ts,
            obj=input_device
        ).order_by('-created')

        data_dict = _prepare_data(data_list)

        if len(data_dict) > MAX_DATA_POINTS:
            data_dict = _thin_out_data_points(data_dict)

        return JsonResponse(data={
            'device': int(input_device), 'unit': data_unit, 'type': data_type, 'data': data_dict,
        })

    else:
        return handler404_api(msg='Only GET method supported')


def _thin_out_data_points(data_dict: dict) -> dict:
    data_point_count = len(data_dict)

    interval = ceil(data_point_count / MAX_DATA_POINTS)

    _winners = dict(islice(enumerate(data_dict), None, None, interval))

    out_dict = {}

    for _ in _winners.values():
        out_dict[_] = data_dict[_]

    return out_dict


def _prepare_data(data_list) -> dict:
    data_dict = {}

    for data_obj in data_list:
        data_dict[datetime.strftime(data_obj.created, DATETIME_TS_FORMAT)] = data_obj.data

    return data_dict


def _get_time(request):
    if 'start_ts' in request.GET:
        start_ts = request.GET['start_ts']

        if 'stop_ts' in request.GET:
            stop_ts = request.GET['stop_ts']

        else:
            stop_ts = add_timezone(request, datetime.now())

    elif 'period' in request.GET and 'period_data' in request.GET:
        period = request.GET['period']
        period_data = int(request.GET['period_data'])

        stop_ts = add_timezone(request, datetime.now())

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
            return handler404_api(msg='Unsupported time period type')

    else:
        return handler404_api(msg='No supported filter provided')

    return start_ts, stop_ts
