# get data for single-condition processing

from core.config.object.data.db import GaDataDb
from core.config.object.device.input import GaInputModel, GaInputDevice
from core.utils.debug import device_log
from core.config.db.template import DEVICE_TMPL

from datetime import timedelta
from datetime import datetime


class Go:
    SQL_QUERY_TIME = DEVICE_TMPL['output']['data']['time']
    SQL_QUERY_RANGE = DEVICE_TMPL['output']['data']['range']

    def __init__(self, condition, device):
        self.condition = condition
        self.database = GaDataDb()
        self.data_list = []
        self.name = device
        self.process_list = []
        self.data_method = None

    def get(self) -> tuple:
        self._get_data()
        device_log(f"Condition match \"{self.condition.name}\" got data \"{self.data_list}\" of type \"{self.data_type}\"", add=self.name, level=7)
        return self.data_list, self.data_type

    def _get_data(self) -> None:
        self.process_list = self._devices_to_process()
        self.data_method = self._get_data_prerequisites()
        self.data_type = self._get_data_type()

        if isinstance(self.condition.check_instance, GaInputModel):
            self._get_data_group()

        else:
            self.data_list = self._get_data_device(device=self.process_list[0])

        if len(self.data_list) == 0:
            device_log(f"No data received for condition match \"{self.condition.name}\" (id \"{self.condition.object_id}\")", add=self.name, level=5)
            raise ValueError(f"Got no data for condition match \"{self.condition.name}\"")

    def _get_data_prerequisites(self):
        # should only run once since its the same for all devices processed
        period_type = self.condition.period
        device_log(f"Condition match \"{self.condition.name}\", period type \"{period_type}\", period \"{self.condition.period_data}\"", add=self.name, level=8)

        if period_type == 'time':
            data_method = self._get_data_by_time

        elif period_type == 'range':
            data_method = self._get_data_by_range

        else:
            device_log(f"Condition match \"{self.condition.name}\" has an unsupported period_type \"{period_type}\"", add=self.name, level=4)
            raise ValueError(f"Unsupported period type for condition match \"{self.condition.name}\"")

        return data_method

    def _get_data_group(self) -> None:
        for device in self.process_list:
            self.data_list.extend(self._get_data_device(device))

    def _get_data_device(self, device: GaInputDevice) -> list:
        # must be iterable since it can be called multiple times from the data_group method
        try:
            data_tuple_list = self.data_method(input_id=device.object_id)
            return [self.data_type(data[0]) for data in data_tuple_list]

        except (TypeError, IndexError):
            return []

    def _devices_to_process(self) -> list:
        # todo: area filtering
        to_check = self.condition.check_instance
        to_process = []
        disabled_list = []

        if isinstance(to_check, GaInputModel):
            if to_check.enabled == 1:
                for device in to_check.member_list:
                    if device.enabled == 1:
                        to_process.append(device)

                    else:
                        disabled_list.append(device)

        else:
            if to_check.enabled == 1:
                to_process.append(to_check)

            else:
                disabled_list.append(to_check)

        if len(disabled_list) > 0:
            device_log(f"Condition match \"{self.condition.name}\" has some disabled inputs: \"{disabled_list}\"", add=self.name, level=8)

        if len(to_process) == 0:
            device_log(f"Got no inputs to pull data from for condition match \"{self.condition.name}\"", add=self.name, level=4)
            raise ValueError(f"No data to process for match \"{self.condition.name}\"")

        return to_process

    def _get_data_type(self) -> (bool, float, int, str):
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
            device_log(f"Input device/model \"{self.condition.check_instance.name}\" has an unsupported data data_type set \"{data_type}\"", level=4)
            raise ValueError(f"Unsupported data type for input \"{self.condition.check_instance.name}\"")

        return typ

    def _get_data_by_time(self, input_id: int) -> list:
        time_period = int(self.condition.period_data)
        timestamp_format = '%Y-%m-%d %H:%M:%S'

        start_time = (datetime.now() - timedelta(seconds=time_period)).strftime(timestamp_format)
        stop_time = datetime.now().strftime(timestamp_format)

        data_tuple_list = self.database.get(self.SQL_QUERY_TIME % (input_id, start_time, stop_time))
        return data_tuple_list

    def _get_data_by_range(self, input_id: int) -> list:
        range_count = int(self.condition.period_data)
        data_tuple_list = self.database.get(self.SQL_QUERY_RANGE % (input_id, range_count))
        return data_tuple_list
