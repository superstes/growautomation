# condition link processing

from core.config.object.setting.condition import GaConditionGroup
from core.device.output.condition.single import Go as ConditionResult
from core.device.output.condition.process.link import get_link_result
from core.device.log import device_logger

from collections import Counter


class Go:
    def __init__(self, group):
        self.group = group
        self.logger = device_logger(group.name)

    def go(self) -> bool:
        return self._process_links(group=self.group)

    def _process_links(self, group) -> bool:
        # static group for recursion
        self.logger.write(f"Processing links for condition \"{group.name}\"", level=8)
        group_member_count = len(group.member_list)
        last_result = None

        for process_nr in range(group_member_count):
            link = self._get_link_to_process(group=group)
            result_dict = self._get_link_data(link=link)

            result = self._get_link_data_result(link=link, result_dict=result_dict)

            self._post_process(
                link=link,
                result=result,
                group=group,
                process_nr=process_nr,
                group_member_count=group_member_count
            )

            link.processed = True
            last_result = result

        self.logger.write(f"Result of condition \"{group.name}\": \"{last_result}\" ", level=6)

        return last_result

    def _get_link_data(self, link) -> dict:
        self.logger.write(f"Getting data for link \"{link.name}\"", level=9)

        result_dict = {}

        # process all conditions in link
        for order, condition in link.member_dict.items():
            if isinstance(condition, GaConditionGroup):
                # if group -> run function recursively
                result_dict[order] = self._process_links(group=condition)

            else:
                if condition.data is not None:
                    # get its data from a previous link-result if it is set
                    result_dict[order] = condition.data
                else:
                    # else process the condition
                    result_dict[order] = ConditionResult(condition=condition, device=self.group.name).get()

        self.logger.write(f"Data of condition-link \"{link.name}\": \"{result_dict}\"", level=8)

        return result_dict

    def _get_link_data_result(self, link, result_dict: dict) -> bool:
        # get the link result via processing its child-results and comparing them via the link-operator

        self.logger.write(f"Getting result of condition-link \"{link.name}\"", level=9)

        try:
            result = get_link_result(
                link=link,
                result_dict=result_dict,
                device=self.group.name
            )

            self.logger.write(f"Result of condition-link \"{link.name}\": \"{result}\"", level=7)
            return result

        except (KeyError, ValueError) as error_msg:
            return self._error(error_exception=error_msg)

    def _get_link_to_process(self, group):
        single_link_member_list = self._get_single_link_member_list(group=group)

        for link in group.member_list:
            if link.processed is False and single_link_member_list[0] in link.member_dict.values():
                return link

    def _post_process(self, link, result: bool, group, process_nr: int, group_member_count: int):
        # check which of the two child-conditions will be further processed

        self.logger.write(f"Post-process of condition \"{group.name}\", link \"{link.name}\", result \"{result}\", process_nr \"{process_nr}\", group_member_count \"{group_member_count}\"", level=9)

        slm_list = self._get_single_link_member_list(group=group)
        nslm = False

        for condition in link.member_dict.values():
            if condition not in slm_list:
                # if the condition will be further processed -> update its data to the link result

                self.logger.write(f"Updating data for condition \"{condition.name}\" to result \"{result}\"", level=9)

                condition.data = result
                nslm = True

        if process_nr != group_member_count and not nslm:
            # error if
            # 1. there is more than one condition that should be further processed
            # or 2. there is no condition that should be further processed and the link is not the last one
            # log error or whatever
            self.logger.write(f"Link \"{link.name}\" (id \"{link.object_id}\") has only single members \"{link.member_dict}\" and is not the last one to process", level=4)
            self._error(RuntimeError(f"Link with id \"{link.object_id}\" is not the last to process but it does not have any link-neighbors."))

    def _get_single_link_member_list(self, group) -> list:
        # we must always start at a link that has one object within it, which only has THIS link

        self.logger.write(f"Getting single link members for condition \"{group.name}\"", level=9)

        lm_list = []
        slm_list = []

        for link in group.member_list:
            if not link.processed:
                lm_list.extend(link.member_dict.values())

        counted = Counter(lm_list)

        for instance, count in counted.items():
            if count == 1:
                slm_list.append(instance)

        self.logger.write(f"Condition \"{group.name}\" has the following single link members \"{slm_list}\"", level=8)

        return slm_list

    def _error(self, error_exception):
        self._reset_flags(group=self.group)
        raise error_exception

    def _reset_flags(self, group):
        self.logger.write(f"Resetting flags for condition \"{group.name}\"", level=9)

        for link in group.member_list:
            link.processed = False
            for condition in link.member_dict.values():
                condition.data = None
