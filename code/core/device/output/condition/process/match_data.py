# get data for single-condition processing

from core.config.object.data.db import GaDataDb
from core.device.log import device_logger
from core.config.db.template import DEVICE_DICT

from datetime import timedelta
from datetime import datetime


class Go:
    SQL_QUERY_TIME = DEVICE_DICT['output']['data']['time']
    SQL_QUERY_RANGE = DEVICE_DICT['output']['data']['range']

    def __init__(self, condition, device):
        self.condition = condition
        self.database = GaDataDb()
        self.data_list = []
        self.logger = device_logger(addition=device)

    def get(self):
        self._get_data_list()

        self.logger.write("Condition item \"%s\" got data \"%s\" of type \"%s\"" % (self.condition.name, self.data_list, self.data_type), level=9)

        return self.data_list, self.data_type

    def _get_data_list(self):
        period_type = self.condition.period

        self.logger.write("Condition item \"%s\", period type \"%s\", period \"%s\"" % (self.condition.name, period_type, self.condition.period_data), level=7)

        if period_type == 'time':
            data = self._get_data_by_time()

        elif period_type == 'range':
            data = self._get_data_by_range()

        else:
            self.logger.write("Condition item \"%s\" has an unsupported period_type \"%s\"" % (self.condition.name, period_type), level=4)
            raise KeyError(f"Unsupported period type for condition match \"{self.condition.name}\"")

        if data is None:
            self.logger.write("No data received for condition item \"%s\" (id \"%s\")" % (self.condition.name, self.condition.object_id), level=5)
            raise ValueError(f"Got no data for condition match \"{self.condition.name}\"")
            # maybe we should let the user decide which data to use if none is found

        self.data_type = self._get_data_type(data=data)

        for tup in data:
            # we will need the obj_id (index 1) to filter on area => Ticket#10
            self.data_list.append(self.data_type(tup[0]))

    def _get_data_type(self, data: list) -> (bool, float, int, str):
        data_type = self.condition.check_instance.datatype

        if data_type == 'bool':
            typ = bool

        elif data_type == 'float':
            typ = float

        elif data_type == 'int':
            typ = int

        elif data_type == 'str':
            typ = str

        else:
            self.logger.write("Input device/model \"%s\" has an unsupported data data_type set \"%s\""
                              % (self.condition.check_instance.name, data_type), level=4)
            raise KeyError(f"Unsupported data type for input \"{self.condition.check_instance.name}\"")

        self.logger.write("Condition item \"%s\", data \"%s\", type \"%s\"" % (self.condition.name, data, typ), level=9)

        return typ

    def _get_data_by_time(self) -> list:
        time_period = int(self.condition.period_data)
        object_id = self.condition.check_instance.object_id
        timestamp_format = '%Y-%m-%d %H:%M:%S'

        start_time = (datetime.now() - timedelta(seconds=time_period)).strftime(timestamp_format)
        stop_time = datetime.now().strftime(timestamp_format)

        data_tuple_list = self.database.get(self.SQL_QUERY_TIME % (object_id, start_time, stop_time))
        return data_tuple_list

    def _get_data_by_range(self) -> list:
        range_count = int(self.condition.period_data)
        object_id = self.condition.check_instance.object_id

        data_tuple_list = self.database.get(self.SQL_QUERY_RANGE % (object_id, range_count))
        return data_tuple_list
