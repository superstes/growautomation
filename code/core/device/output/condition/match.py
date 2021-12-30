# handles single condition processing

from core.utils.debug import device_log
from core.device.output.condition.match_data import Go as MatchData
from core.device.output.condition.match_special import Go as SpecialMatch
from core.config.object.setting.condition import GaConditionMatchSpecial


class Go:
    def __init__(self, condition, device: str):
        self.condition = condition
        self.data_list = []
        self.data_type = None
        self.device = device

    def get(self) -> bool:
        device_log(f"Getting data of condition match \"{self.condition.name}\"", add=self.device, level=9)

        if isinstance(self.condition.check_instance, GaConditionMatchSpecial):
            return SpecialMatch(condition=self.condition, device=self.device).get()

        self.data_list, self.data_type = MatchData(condition=self.condition, device=self.device).get()

        if self.data_type in [int, float]:
            data = self._get_data()

        else:
            # maybe add more functionality for non-number data types (?)
            data = self.data_list[0]

        device_log(f"Data of condition match \"{self.condition.name}\": \"{data}\"", add=self.device, level=8)
        result = self._compare_data(data=data)
        device_log(f"Result of condition match \"{self.condition.name}\": \"{result}\"", add=self.device, level=7)
        return result

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
            device_log(f"Failed to apply data type \"{self.data_type}\" to data \"{data}\" or value \"{self.condition.value}\" "
                       f"of condition match \"{self.condition.name}\"", add=self.device, level=3)
            raise ValueError(f"Unsupported data type \"{self.data_type}\" for condition match \"{self.condition.name}\"")

        if operator == '=':
            if value == data:
                result = True

        elif operator == '!=':
            if value != data:
                result = True

        elif operator == '>' and self.data_type in [int, float]:
            if value > data:
                result = True

        elif operator == '<' and self.data_type in [int, float]:
            if value < data:
                result = True

        else:
            device_log(f"Condition match \"{self.condition.name}\" has an unsupported operator \"{operator}\" with value_type \"{self.data_type}\"", add=self.device, level=4)
            raise ValueError(f"Unsupported operator for condition \"{self.condition.name}\"")

        device_log(f"Condition match \"{self.condition.name}\" result for comparison \"{value} {operator} {data}\" = {result}", add=self.device, level=8)
        return result

    def _get_data(self) -> (float, int):
        value_check = self.condition.calc
        if value_check == 'min':
            data = min(self.data_list)

        elif value_check == 'max':
            data = max(self.data_list)

        elif value_check == 'avg':
            data = (sum(self.data_list) / len(self.data_list))

        else:
            device_log(f"Condition match \"{self.condition.name}\" has an unsupported value_check set: \"{value_check}\"", add=self.device, level=4)
            raise ValueError(f"Unsupported check type for condition \"{self.condition.name}\"")

        device_log(f"Data of condition match \"{self.condition.name}\" using value check \"{value_check}\": {data}", add=self.device, level=8)

        return data
