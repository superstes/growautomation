# checks conditions

from core.config.object.data.db import GaDataDb
from core.utils.debug import debugger
from core.config.db.template import DEVICE_DICT

from datetime import timedelta
from datetime import datetime


class Go:
    SQL_QUERY_TIME = DEVICE_DICT['output']['data']['time']
    SQL_QUERY_RANGE = DEVICE_DICT['output']['data']['range']
    SPECIAL_TIME_FORMAT = '%H:%M:%S'
    SPECIAL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, condition):
        self.database = GaDataDb()
        self.condition = condition
        self.data_list = []
        self.data_type = None

    def get(self) -> bool:
        if self.condition.special is None:
            data_list, value_type = self._get_data_list()

            if value_type in [int, float]:
                data = self._get_data()
            else:
                data = data_list[0]

            return self._compare_data(data=data)
        else:
            return self._special()

    def _special(self) -> bool:
        speci = self.condition.special
        error = False

        if speci in ['time', 'datetime']:
            self.data_type = datetime
            data = datetime.now()

            if speci == 'time':
                value = datetime.strptime(self.condition.value, self.SPECIAL_TIME_FORMAT)
            elif speci == 'datetime':
                value = datetime.strptime(self.condition.value, self.SPECIAL_DATETIME_FORMAT)
            else:
                error = True
        else:
            error = True

        if error:
            # log error or whatever
            debugger("device-output-condition-proc-cond | _special | condition '%s' has an unsupported "
                     "special type '%s'" % (self.condition.name, speci))
            raise KeyError("Condition '%s' has an unsupported special type '%s" % (self.condition.name, speci))

        return self._compare_data(data=data, speci_value=value)

    def _compare_data(self, data, speci_value=None) -> bool:
        operator = self.condition.operator
        if speci_value is not None:
            value = speci_value
        else:
            value = self.data_type(self.condition.value)

        result = False

        if operator == '=':
            if value == data:
                result = True
        elif operator == '!=':
            if value != data:
                result = True
        elif operator == '>' and self.data_type in [int, float, datetime]:
            if data > value:
                result = True
        elif operator == '<' and self.data_type in [int, float, datetime]:
            if data < value:
                result = True
        else:
            # log error or whatever
            debugger("device-output-condition-proc-cond | _compare_data | condition '%s' has an unsupported "
                     "operator '%s' with value_type '%s'" % (self.condition.name, operator, self.data_type))
            raise KeyError("Condition '%s' has an unsupported operator '%s" % (self.condition.name, operator))

        return result

    def _get_data(self) -> (float, int):
        value_check = self.condition.value_check

        if value_check == 'min':
            data = self._data_min(data_list=self.data_list)
        elif value_check == 'max':
            data = self._data_max(data_list=self.data_list)
        elif value_check == 'avg':
            data = self._data_avg(data_list=self.data_list)
        else:
            # log error or whatever
            debugger("device-output-condition-proc-cond | get_condition_result | condition '%s' has an unsupported "
                     "value_check '%s" % (self.condition.name, value_check))
            raise KeyError("Condition '%s' has an unsupported value_check '%s'" % (self.condition.name, value_check))

        return data

    @staticmethod
    def _data_min(data_list: (int, float)) -> (int, float):
        mini = min(data_list)
        return mini

    @staticmethod
    def _data_max(data_list: (int, float)) -> (int, float):
        maxi = max(data_list)
        return maxi

    @staticmethod
    def _data_avg(data_list: (int, float)) -> (int, float):
        avg = sum(data_list) / len(data_list)
        return avg

    def _get_data_list(self):
        period_type = self.condition.period_type

        if period_type == 'time':
            data = self._get_data_by_time()
        elif period_type == 'range':
            data = self._get_data_by_range()
        else:
            # log error or whatever
            debugger("device-output-condition-proc-cond | _get_data_list | condition '%s' has an unsupported "
                     "period_type '%s" % (self.condition.name, period_type))
            raise KeyError("Condition '%s' has an unsupported period_type '%s'" % (self.condition.name, period_type))

        self._get_data_type(data=data)

        for tup in data:
            self.data_list.append(self.data_type(tup[0]))

    def _get_data_type(self, data: list):
        self.data_type = data[0][1]

        if self.data_type == 'bool':
            typ = bool
        if self.data_type == 'float':
            typ = float
        elif self.data_type == 'int':
            typ = int
        elif self.data_type == 'str':
            typ = str
        else:
            raise KeyError("Condition '%s' has an unsupported data value_type '%s'"
                           % (self.condition.name, self.data_type))

        return typ

    def _get_data_by_time(self) -> list:
        time_period = self.condition.period
        object_id = self.condition.check_instance.object_id
        timestamp_format = '%Y-%m-%d %H:%M:%S'

        start_time = (datetime.now() - timedelta(seconds=time_period)).strftime(timestamp_format)
        stop_time = datetime.now().strftime(timestamp_format)

        data_tuple_list = self.database.get(self.SQL_QUERY_TIME % (object_id, start_time, stop_time))

        return data_tuple_list

    def _get_data_by_range(self) -> list:
        range_count = self.condition.period
        object_id = self.condition.check_instance.object_id

        data_tuple_list = self.database.get(self.SQL_QUERY_RANGE % (object_id, range_count))

        return data_tuple_list

    @staticmethod
    def _get_data_datetime() -> datetime:
        current_time = datetime.now()

        return current_time
