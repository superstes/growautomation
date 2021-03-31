# handles single condition processing

from core.device.log import device_logger
# from core.device.output.condition.process.single_special import special as SpecialData
# Ticket#23
from core.device.output.condition.process.match_data import Go as DefaultData

from datetime import datetime


class Go:
    def __init__(self, condition, device: str):
        self.condition = condition
        self.data_list = []
        self.data_type = None
        self.logger = device_logger(addition=device)
        self.device = device

    def get(self) -> bool:
        self.logger.write(f"Getting data for condition match \"{self.condition.name}\"", level=9)
        self.data_list, self.data_type = DefaultData(condition=self.condition, device=self.device).get()

        if self.data_type in [int, float]:
            data = self._get_data()

        else:
            data = self.data_list[0]

        result = self._compare_data(data=data)
        self.logger.write(f"Result of condition match \"{self.condition.name}\": \"{result}\"", level=6)
        return result

        # Ticket#23
        # data, value = SpecialData(
        #     condition=self.condition,
        #     device=self.device
        # )
        # return self._compare_data(data=data, speci_value=value)

    def _compare_data(self, data) -> bool:
        operator = self.condition.operator
        value = self.data_type(self.condition.value)
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
        value_check = self.condition.check
        self.logger.write("Getting data for condition item \"%s\" while using value_check \"%s\"" % (self.condition.name, value_check), level=9)

        if value_check == 'min':
            data = min(self.data_list)

        elif value_check == 'max':
            data = max(self.data_list)

        elif value_check == 'avg':
            data = (sum(self.data_list) / len(self.data_list))

        else:
            self.logger.write("Condition item \"%s\" has an unsupported value_check set: \"%s\"" % (self.condition.name, value_check), level=4)
            raise KeyError("Condition \"%s\" has an unsupported value_check \"%s\"" % (self.condition.name, value_check))

        return data
