from django.http import JsonResponse
from datetime import timedelta
from math import ceil
from django.db.models import QuerySet

from ....models import InputDataModel, ObjectInputModel, GroupInputModel
from ...handlers import handler400_api, handler500_api
from ....utils.basic import get_dt_w_tz
from ....utils.helper import get_device_parent_setting, get_instance_from_id
from ....utils.auth import method_user_passes_test
from ....user import authorized_to_read
from ....config import shared as config


class ApiData:
    MEASURE_TS_FORMAT = '%H:%M:%S:%f'
    THIN_OUT_FUNCTIONS = ['avg', 'max', 'min']

    def __init__(self, request, input_id: int = None, period: str = None, period_data: int = None, start_ts: str = None, stop_ts: str = None,
                 return_dict: bool = False, input_type=None):
        self.request = request
        self.input_id = input_id
        self.input_type = input_type
        self.return_dict = return_dict
        self.error = None
        self.measurement = []

        if (period is not None or start_ts is not None) and input_id is not None:
            self.data = {'period': period, 'period_data': period_data, 'start_ts': start_ts, 'stop_ts': stop_ts}

        else:
            self.data = request.GET

    @method_user_passes_test(authorized_to_read, login_url=config.LOGIN_URL)
    def go(self) -> (dict, JsonResponse):
        if self.request.method == 'GET':
            if self.input_id is None:
                if 'input_device' in self.data:
                    self.input_id = int(self.data['input_device'])
                    self.input_type = ObjectInputModel

                elif 'input_model' in self.data:
                    self.input_id = int(self.data['input_model'])
                    self.input_type = GroupInputModel

                else:
                    return handler400_api(msg='Need to specify either input_device or input_model')

            return self.get()

        else:
            return handler400_api(msg='Only GET method supported')

    def get(self):
        input_obj = get_instance_from_id(typ=self.input_type, obj=self.input_id)
        data_unit = get_device_parent_setting(child_obj=input_obj, setting='unit')
        data_type = get_device_parent_setting(child_obj=input_obj, setting='datatype')

        _time = self._get_time()

        if type(_time) != tuple:
            return handler500_api(msg='Error processing time period')

        start_ts, stop_ts = _time

        time_span = stop_ts - start_ts
        if time_span > timedelta(days=365):
            if self.request.user_agent.is_mobile:
                max_data_points = config.DB_MAX_DATA_POINTS_HUGE_CLI
            else:
                max_data_points = config.DB_MAX_DATA_POINTS_HUGE_MOBILE

        elif time_span > timedelta(days=30):
            if self.request.user_agent.is_mobile:
                max_data_points = config.DB_MAX_DATA_POINTS_LONG_CLI
            else:
                max_data_points = config.DB_MAX_DATA_POINTS_LONG_MOBILE

        elif time_span > timedelta(days=7):
            if self.request.user_agent.is_mobile:
                max_data_points = config.DB_MAX_DATA_POINTS_MEDIUM_CLI
            else:
                max_data_points = config.DB_MAX_DATA_POINTS_MEDIUM_MOBILE

        else:
            if self.request.user_agent.is_mobile:
                max_data_points = config.DB_MAX_DATA_POINTS_SHORT_CLI
            else:
                max_data_points = config.DB_MAX_DATA_POINTS_SHORT_MOBILE

        query_result = InputDataModel.objects.filter(
            created__gte=start_ts,
            created__lte=stop_ts,
            obj=input_obj
        ).order_by('-created').values(
            'created', 'data',
        )

        query_result = self._prepare_data(query_result=self._thin_out_data_points(
            query_result,
            wanted=max_data_points,
            existing=query_result.count(),
            data_type=data_type
        ))

        json_dict = {
            'device_id': int(self.input_id), 'device_name': input_obj.name, 'data_unit': data_unit, 'data_type': data_type, 'error': self.error,
            'xy_data': query_result, 'measurement': self.measurement,
        }

        if self.return_dict:
            return json_dict

        else:
            return JsonResponse(data=json_dict)

    @classmethod
    def _thin_out_data_points(cls, query_result: QuerySet, wanted: int, existing: int, calc: str = 'avg', data_type: str = 'float') -> dict:
        """
        :param query_result: QuerySet({created: _, data: _})
        :param wanted: Data points wanted
        :param calc: Function to apply to the filtered data points
        :return: filtered data
        :rtype: dict
        """
        interval = ceil(existing / wanted)
        calc = calc if calc in cls.THIN_OUT_FUNCTIONS else 'avg'
        calc_datatypes = [int, float]

        if data_type == 'int':
            data_type = int

        elif data_type == 'bool':
            data_type = bool

        elif data_type == 'str':
            data_type = str

        else:
            data_type = float

        filtered = {}
        counter = 0
        tmp = {}

        for dataset in query_result:
            if counter % interval == 0 and counter != 0:
                if data_type in calc_datatypes:
                    if calc == 'avg':
                        index = ceil(counter / 2)
                        filtered[list(tmp.keys())[index]] = "{:.2f}".format(sum(tmp.values()) / counter)

                    elif calc == 'max':
                        max_val = max(tmp.values())
                        filtered[[time for time, data in tmp.items() if data == max_val][0]] = max_val

                    else:
                        min_val = min(tmp.values())
                        filtered[[time for time, data in tmp.items() if data == min_val][0]] = min_val

                    tmp = {}
                    counter = 0

                else:
                    filtered[dataset['created']] = data_type(dataset['data'])

            if data_type in calc_datatypes:
                tmp[dataset['created']] = data_type(dataset['data'])

            counter += 1

        return filtered

    @staticmethod
    def _prepare_data(query_result: dict) -> list:
        # conversions for usage with chartjs:
        #   1. datetime to utc millisecond-timestamp
        #   2. data to x/y format
        return [
            {
                'x': round(time.timestamp() * 1000),
                'y': data
             }
            for time, data in query_result.items()
        ]

    def _get_time(self):
        start_ts, _start_ts = None, None
        stop_ts, _stop_ts = None, None
        _period, _period_data = None, None

        if 'stop_ts' in self.data:
            _stop_ts = self.data['stop_ts']

        stop_ts = get_dt_w_tz(naive=_stop_ts)

        if 'period' in self.data and 'period_data' in self.data:
            # todo: support for 'last week' etc. (period=d,data=7,shift=d,shift_data:7)  => Ticket#33
            _period = self.data['period']
            _period_data = int(self.data['period_data'])

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

        else:
            if 'start_ts' in self.data:
                start_ts = get_dt_w_tz(naive=self.data['start_ts'])

        if start_ts is None:
            return handler400_api(msg='No supported time period provided')

        else:
            return start_ts, stop_ts
