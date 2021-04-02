# handles single condition processing

from core.device.log import device_logger
from core.device.output.condition.process.match_data import Go as MatchData

from datetime import datetime


class Go:
    def __init__(self, condition, device: str):
        self.condition = condition
        self.data_list = []
        self.data_type = None
        self.logger = device_logger(addition=device)
        self.device = device

    def get(self) -> bool:
        self.logger.write(f"Getting data of condition match \"{self.condition.name}\"", level=9)
        self.data_list, self.data_type = MatchData(condition=self.condition, device=self.device).get()

        if self.data_type in [int, float]:
            data = self._get_data()

        else:
            # maybe add more functionality for non-number data types (?)
            data = self.data_list[0]

        self.logger.write(f"Data of condition match \"{self.condition.name}\": \"{data}\"", level=6)  # 7
        result = self._compare_data(data=data)
        self.logger.write(f"Result of condition match \"{self.condition.name}\": \"{result}\"", level=6)
        return result

        # todo: special-cases => Ticket#23
        # from core.device.output.condition.process.single_special import special as SpecialData
        # data, value = SpecialData(
        #     condition=self.condition,
        #     device=self.device
        # )
        # return self._compare_data(data=data, speci_value=value)

    def _compare_data(self, data) -> bool:
        operator = self.condition.operator
        result = False

        try:
            if self.data_type == float:
                value = round(self.data_type(self.condition.value), 2)
                data = round(self.data_type(data), 2)

            else:
                value = self.data_type(self.condition.value)

        except TypeError:
            self.logger.write(f"Failed to apply data type \"{self.data_type}\" to data \"{data}\" or value \"{self.condition.value}\" "
                              f"of condition match \"{self.condition.name}\"", level=3)
            raise KeyError(f"Unsupported data type \"{self.data_type}\" for condition match \"{self.condition.name}\"")

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
            self.logger.write(f"Condition match \"{self.condition.name}\" has an unsupported operator \"{operator}\" "
                              f"with value_type \"{self.data_type}\"", level=4)
            raise KeyError(f"Unsupported operator for condition \"{self.condition.name}\"")

        self.logger.write(f"Condition match \"{self.condition.name}\" result for comparison \"{value} {operator} {data}\" = {result}", level=6)  # 7
        return result

    def _get_data(self) -> (float, int):
        value_check = self.condition.check
        if value_check == 'min':
            data = min(self.data_list)

        elif value_check == 'max':
            data = max(self.data_list)

        elif value_check == 'avg':
            data = (sum(self.data_list) / len(self.data_list))

        else:
            self.logger.write(f"Condition match \"{self.condition.name}\" has an unsupported value_check set: \"{value_check}\"", level=4)
            raise KeyError(f"Unsupported check type for condition \"{self.condition.name}\"")

        self.logger.write(f"Data of condition match \"{self.condition.name}\" using value check \"{value_check}\": {data}", level=6)  # 7

        return data
