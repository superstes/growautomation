# handles single condition processing

from core.device.log import device_logger
from core.device.output.condition.process.single_special import special as SpecialData
from core.device.output.condition.process.single_data import Go as DefaultData

from datetime import datetime


class Go:
    def __init__(self, condition, device: str):
        self.condition = condition
        self.data_list = []
        self.data_type = None
        self.logger = device_logger(addition=device)
        self.device = device

    def get(self) -> bool:
        self.logger.write("Getting data for condition item \"%s\"" % self.condition.name, level=9)

        if self.condition.condition_special is None:
            self.data_list, self.data_type = DefaultData(condition=self.condition, device=self.device).get()

            if self.data_type in [int, float]:
                data = self._get_data()
            else:
                data = self.data_list[0]

            return self._compare_data(data=data)
        else:
            data, value = SpecialData(
                condition=self.condition,
                device=self.device
            )
            return self._compare_data(data=data, speci_value=value)

    def _compare_data(self, data, speci_value=None) -> bool:
        operator = self.condition.condition_operator

        if speci_value is not None:
            value = speci_value
        else:
            value = self.data_type(self.condition.condition_value)

        self.logger.write("Condition item \"%s\" comparing data: \"%s %s %s\"" % (self.condition.name, data, operator, value), level=9)

        result = False

        if operator == '=':
            if value == data:
                result = True
        elif operator == '!=':
            if value != data:
                result = True
        elif operator == '>' and self.data_type in [int, float, datetime]:
            if value > data:
                result = True
        elif operator == '<' and self.data_type in [int, float, datetime]:
            if value < data:
                result = True
        else:
            self.logger.write("Condition item \"%s\" has an unsupported operator \"%s\" with value_type \"%s\""
                              % (self.condition.name, operator, self.data_type), level=4)
            raise KeyError("Condition \"%s\" has an unsupported operator \"%s\"" % (self.condition.name, operator))

        self.logger.write("Condition item \"%s\" result for comparison \"%s %s %s\" => \"%s\"" % (self.condition.name, data, operator, value, result), level=7)

        return result

    def _get_data(self) -> (float, int):
        value_check = self.condition.condition_check

        self.logger.write("Getting data for condition item \"%s\" while using value_check \"%s\"" % (self.condition.name, value_check), level=9)

        if value_check == 'min':
            data = self._data_min(data_list=self.data_list)
        elif value_check == 'max':
            data = self._data_max(data_list=self.data_list)
        elif value_check == 'avg':
            data = self._data_avg(data_list=self.data_list)
        else:
            self.logger.write("Condition item \"%s\" has an unsupported value_check set: \"%s\"" % (self.condition.name, value_check), level=4)
            raise KeyError("Condition \"%s\" has an unsupported value_check \"%s\"" % (self.condition.name, value_check))

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
