# handles single condition processing

from core.utils.debug import debugger
from core.device.output.condition.process.single_special import special as SpecialData
from core.device.output.condition.process.single_data import Go as DefaultData

from datetime import datetime


class Go:
    def __init__(self, condition):
        self.condition = condition
        self.data_list = []
        self.data_type = None

    def get(self) -> bool:
        debugger("device-output-condition-single | get | getting data for condition \"%s\"" % self.condition.name)

        if self.condition.condition_special is None:
            self.data_list, self.data_type = DefaultData(condition=self.condition).get()

            if self.data_type in [int, float]:
                data = self._get_data()
            else:
                data = self.data_list[0]

            return self._compare_data(data=data)
        else:
            data, value = SpecialData(
                condition=self.condition
            )
            return self._compare_data(data=data, speci_value=value)

    def _compare_data(self, data, speci_value=None) -> bool:
        operator = self.condition.condition_operator

        if speci_value is not None:
            value = speci_value
        else:
            value = self.data_type(self.condition.condition_value)

        debugger("device-output-condition-single | _compare_data | condition \"%s\", data '%s %s', operator \"%s\""
                 % (self.condition.name, type(data), data, operator))

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
            # log error or whatever
            debugger("device-output-condition-single | _compare_data | condition \"%s\" has an unsupported "
                     "operator \"%s\" with value_type \"%s\"" % (self.condition.name, operator, self.data_type))
            raise KeyError("Condition \"%s\" has an unsupported operator \"%s\"" % (self.condition.name, operator))

        debugger("device-output-condition-single | _compare_data | condition \"%s\", data \"%s\" \"%s\", operator \"%s\", "
                 "value '%s %s', result \"%s\""
                 % (self.condition.name, type(data), data, operator, type(value), value, result))

        return result

    def _get_data(self) -> (float, int):
        value_check = self.condition.condition_check

        debugger("device-output-condition-single | _get_data | condition \"%s\", value_check \"%s\""
                 % (self.condition.name, value_check))

        if value_check == 'min':
            data = self._data_min(data_list=self.data_list)
        elif value_check == 'max':
            data = self._data_max(data_list=self.data_list)
        elif value_check == 'avg':
            data = self._data_avg(data_list=self.data_list)
        else:
            # log error or whatever
            debugger("device-output-condition-single | _get_data | condition \"%s\" has an unsupported "
                     "value_check \"%s\"" % (self.condition.name, value_check))
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
