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

        debugger("device-output-condition-proc-single | get | condition \"%s\", data \"%s\", type \"%s\""
                 % (self.condition.name, self.data_list, self.data_type))

        return self.data_list, self.data_type

    def _get_data_list(self):
        period_type = self.condition.condition_period

        debugger("device-output-condition-proc-single | _get_data_type | condition \"%s\", period type \"%s\", period \"%s\""
                 % (self.condition.name, period_type, self.condition.condition_period_data))

        if period_type == 'time':
            data = self._get_data_by_time()
        elif period_type == 'range':
            data = self._get_data_by_range()
        else:
            # log error or whatever
            debugger("device-output-condition-proc-single | _get_data_list | condition \"%s\" has an unsupported "
                     "period_type '%s" % (self.condition.name, period_type))
            raise KeyError("Condition \"%s\" has an unsupported period_type \"%s\"" % (self.condition.name, period_type))

        if data is None:
            raise ValueError("No data received for single condition \"%s\" (id \"%s\")"
                             % (self.condition.name, self.condition.object_id))
        # maybe we should let the user decide which data to use if none is found

        self.data_type = self._get_data_type(data=data)

        for tup in data:
            self.data_list.append(self.data_type(tup[0]))

    def _get_data_type(self, data: list):
        self.data_type = data[0][1]

        if self.data_type == 'bool':
            typ = bool
        elif self.data_type == 'float':
            typ = float
        elif self.data_type == 'int':
            typ = int
        elif self.data_type == 'str':
            typ = str
        else:
            raise KeyError("Condition \"%s\" has an unsupported data value_type \"%s\""
                           % (self.condition.name, self.data_type))

        debugger("device-output-condition-proc-single | _get_data_type | condition \"%s\", data \"%s\", type \"%s\""
                 % (self.condition.name, data, typ))

        return typ

    def _get_data_by_time(self) -> list:
        time_period = int(self.condition.condition_period_data)
        object_id = self.condition.check_instance.object_id
        timestamp_format = '%Y-%m-%d %H:%M:%S'

        start_time = (datetime.now() - timedelta(seconds=time_period)).strftime(timestamp_format)
        stop_time = datetime.now().strftime(timestamp_format)

        data_tuple_list = self.database.get(self.SQL_QUERY_TIME % (object_id, start_time, stop_time))

        return data_tuple_list

    def _get_data_by_range(self) -> list:
        range_count = int(self.condition.condition_period_data)
        object_id = self.condition.check_instance.object_id

        data_tuple_list = self.database.get(self.SQL_QUERY_RANGE % (object_id, range_count))

        return data_tuple_list
