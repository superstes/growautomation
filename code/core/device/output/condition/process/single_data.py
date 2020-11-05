# get data for single-condition processing

from core.config.object.data.db import GaDataDb
from core.utils.debug import debugger
from core.config.db.template import DEVICE_DICT

from datetime import timedelta
from datetime import datetime


class Go:
    SQL_QUERY_TIME = DEVICE_DICT['output']['data']['time']
    SQL_QUERY_RANGE = DEVICE_DICT['output']['data']['range']

    def __init__(self, condition):
        self.condition = condition
        self.database = GaDataDb()
        self.data_list = []

    def get(self):
        self._get_data_list()
        return self.data_list, self.data_type

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
