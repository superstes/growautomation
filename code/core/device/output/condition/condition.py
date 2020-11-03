# processes conditions for output execution

from core.device.output.condition.group import get as get_main_group_list
from core.device.output.condition.link import Go as GetGroupResult


class Go:
    def __init__(self, instance, reverse: bool = False):
        self.instance = instance
        # self.reverse = reverse
        # todo: need to check how the reversing of outputs via condition should be handled

    @staticmethod
    def get() -> dict:
        main_group_list = get_main_group_list()
        group_result_dict = {}

        for group in main_group_list:
            group_result_dict[group] = GetGroupResult(group=group).go()

        return group_result_dict
