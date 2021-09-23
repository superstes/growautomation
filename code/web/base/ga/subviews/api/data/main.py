from django.http import JsonResponse
from datetime import datetime, timedelta
from math import ceil
from pytz import utc as pytz_utc

from ....models import InputDataModel, ObjectInputModel, GroupInputModel
from ...handlers import handler400_api, handler500_api
from ....utils.helper import get_device_parent_setting, add_timezone, get_instance_from_id, get_datetime_w_tz, get_controller_setting, develop_log
from ....utils.main import method_user_passes_test
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
        develop_log(request=self.request, output=f"{stop_ts.strftime('%H:%M:%S:%f')}")

        time_span = stop_ts - start_ts
        if time_span > timedelta(days=365):
            if self.request.user_agent.is_mobile:
                max_data_points = config.MAX_DATA_POINTS_HUGE_CLI
            else:
                max_data_points = config.MAX_DATA_POINTS_HUGE_MOBILE

        elif time_span > timedelta(days=30):
            if self.request.user_agent.is_mobile:
                max_data_points = config.MAX_DATA_POINTS_LONG_CLI
            else:
                max_data_points = config.MAX_DATA_POINTS_LONG_MOBILE

        elif time_span > timedelta(days=7):
            if self.request.user_agent.is_mobile:
                max_data_points = config.MAX_DATA_POINTS_MEDIUM_CLI
            else:
                max_data_points = config.MAX_DATA_POINTS_MEDIUM_MOBILE

        else:
            if self.request.user_agent.is_mobile:
                max_data_points = config.MAX_DATA_POINTS_SHORT_CLI
            else:
                max_data_points = config.MAX_DATA_POINTS_SHORT_MOBILE

        self._add_measurement('Pulling data')
        data_list = InputDataModel.objects.filter(
            created__gte=start_ts,
            created__lte=stop_ts,
            obj=input_obj
        ).order_by('-created')

        self._add_measurement('Preparing data')
        data_dict = self._prepare_data(data_list=data_list, data_type=data_type)

        self._add_measurement('Thinning data')
        if len(data_dict) > max_data_points:
            data_dict = self._thin_out_data_points(data_dict, wanted=max_data_points)

        self._add_measurement('Post processing')
        xy_data_list = []
        for time, data in data_dict.items():
            xy_data_list.append({'x': time, 'y': data})

        json_dict = {
            'device_id': int(self.input_id), 'device_name': input_obj.name, 'data_unit': data_unit, 'data_type': data_type, 'error': self.error,
            'xy_data': xy_data_list, 'measurement': self.measurement,
        }

        if self.return_dict:
            return json_dict

        else:
            return JsonResponse(data=json_dict)

    def _add_measurement(self, msg: str):
        # for troubleshooting
        self.measurement.append(f'{datetime.now().strftime(self.MEASURE_TS_FORMAT)} | {msg}')

    @classmethod
    def _thin_out_data_points(cls, data_dict: dict, wanted: int, function: str = 'avg') -> dict:
        """
        :param data_dict: {time: data}
        :param wanted: Data points wanted
        :param function: Function to apply to the filtered data points
        :return: filtered data
        :rtype: dict
        """

        data_point_count = len(data_dict)
        interval = ceil(data_point_count / wanted)
        thin_out_function = function if function in cls.THIN_OUT_FUNCTIONS else 'avg'

        filtered = {}
        counter = 0
        tmp = {}
        for key, value in data_dict.items():
            if counter % interval == 0 and len(tmp) != 0:
                if thin_out_function == 'avg':
                    index = ceil(len(tmp) / 2)
                    filtered[list(tmp.keys())[index]] = "{:.2f}".format(sum(tmp.values()) / len(tmp))

                elif thin_out_function == 'max':
                    max_val = max(tmp.values())
                    filtered[[key for key, val in tmp.items() if val == max_val][0]] = max_val

                elif thin_out_function == 'min':
                    min_val = min(tmp.values())
                    filtered[[key for key, val in tmp.items() if val == min_val][0]] = min_val

                tmp = {}

            counter += 1
            tmp[key] = value

        return filtered

    def _prepare_data(self, data_list, data_type: str) -> dict:
        out_dict = {}

        if data_type == 'float':
            typ = float

        elif data_type == 'int':
            typ = int

        elif data_type == 'bool':
            typ = bool

        else:
            typ = str

        own_tz = get_controller_setting(self.request, setting='timezone')
        for data_obj in data_list:
            # converting datetime to utc millisecond-timestamp since that is the default time-format in chartjs
            tz_aware_dt = add_timezone(request=self.request, datetime_obj=data_obj.created, tz=own_tz, ctz=own_tz)
            ts_milli_utc = round(tz_aware_dt.astimezone(pytz_utc).timestamp() * 1000)
            out_dict[ts_milli_utc] = typ(data_obj.data)

        return out_dict

    def _get_time(self):
        start_ts, _start_ts = None, None
        stop_ts, _stop_ts = None, None
        _period, _period_data = None, None

        if 'stop_ts' in self.data:
            _stop_ts = self.data['stop_ts']

        if _stop_ts is not None:
            stop_ts = get_datetime_w_tz(self.request, dt_str=_stop_ts)

        else:
            stop_ts = add_timezone(self.request, datetime_obj=datetime.now())

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
                _start_ts = self.data['start_ts']

            if _start_ts is not None:
                start_ts = get_datetime_w_tz(self.request, dt_str=_start_ts)

        if start_ts is None:
            return handler400_api(msg='No supported time period provided')

        else:
            return start_ts, stop_ts
