# condition link processing

from core.config.object.setting.condition import GaConditionGroup
from core.device.output.condition.single import Go as CondtitionResult
from core.device.output.condition.process.link import get_link_result
from core.utils.debug import debugger

from collections import Counter


class Go:
    def __init__(self, group):
        self.group = group

    def go(self) -> bool:
        return self._process_links(group=self.group)

    def _process_links(self, group) -> bool:
        # static group for recursion
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

        return last_result

    def _get_link_data(self, link) -> dict:
        result_dict = {}
        count = 1

        # process all conditions in link
        for condition in link.member_list:
            if isinstance(condition, GaConditionGroup):
                # if group -> run function recursively
                result_dict[count] = self._process_links(group=condition)

            else:
                if condition.data is not None:
                    # get its data from a previous link-result if it is set
                    result_dict[count] = condition.data
                else:
                    # else process the condition
                    result_dict[count] = CondtitionResult(condition=condition).get()

            count += 1

        return result_dict

    def _get_link_data_result(self, link, result_dict: dict) -> bool:
        # get the link result via processing its child-results and comparing them via the link-operator
        try:
            result = get_link_result(
                link=link,
                result_dict=result_dict
            )
        except (KeyError, ValueError) as error_msg:
            self._error(error_exception=error_msg)

        return result

    def _get_link_to_process(self, group):
        single_link_member_list = self._get_single_link_member_list(group=group)

        for link in group.member_list:
            if link.processed is False and single_link_member_list[0] in link.member_list:
                return link

    def _post_process(self, link, result: bool, group, process_nr: int, group_member_count: int):
        # check which of the two child-conditions will be further processed
        slm_list = self._get_single_link_member_list(group=group)
        nslm = False
        nslm_count = 0

        for condition in link.member_list:
            if condition not in slm_list:
                # if the condition will be further processed -> update its data to the link result
                condition.data = result
                nslm = True
                nslm_count += 1

        if nslm_count != 1 or (not nslm and process_nr != group_member_count):
            # error if
            # 1. there is more than one condition that should be further processed
            # or 2. there is no condition that should be further processed and the link is not the last one
            # log error or whatever
            debugger("device-output-condition-link | _process_links | link '%s' has only single members '%s"
                     % (link.object_id, link.member_list))
            self._error(RuntimeError("Link with id '%s' is not the last to process but it does not have "
                                     "any link-neighbors."))

    @staticmethod
    def _get_single_link_member_list(group) -> list:
        # we must always start at a link that has one object within it, which only hast THIS link
        lm_list = []
        slm_list = []

        for link in group.member_list:
            if not link.processed:
                lm_list.extend(link.member_list)

        counted = Counter(lm_list)

        for instance, count in counted.items():
            if count == 1:
                slm_list.append(instance)

        return slm_list

    def _error(self, error_exception):
        self._reset_flags(group=self.group)
        raise error_exception

    @staticmethod
    def _reset_flags(group):
        for link in group:
            link.processed = False
            for condition in link.member_list:
                condition.data = None
