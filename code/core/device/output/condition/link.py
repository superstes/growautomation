# condition link processing

from core.config.object.setting.condition import GaConditionGroup, GaConditionLink
from core.device.output.condition.match import Go as ConditionResult
from core.utils.debug import device_log

from collections import Counter

LINK_ORDER_ID_1 = 1
LINK_ORDER_ID_2 = 2


class Go:
    def __init__(self, group: GaConditionGroup):
        self.group = group
        self.name = group.name

    def go(self) -> bool:
        """Generic public method
        :return: Final condition result
        :rtype: bool
        """
        return self._process_links(group=self.group)

    def _process_links(self, group: GaConditionGroup) -> bool:
        """Will be called to process links inside of a condition.
        Is used recursively.
        :param group: The condition object
        :type group: GaConditionGroup
        :return: Will return the calculated result of the condition
        :rtype: bool
        """
        device_log(f"Processing links for condition \"{group.name}\"", add=self.name, level=8)
        group_member_count = len(group.member_list)
        last_result = None

        for process_nr in range(1, group_member_count + 1):
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

        device_log(f"Result of condition \"{group.name}\": \"{last_result}\" ", add=self.name, level=6)
        self._reset_flags(group)

        return last_result

    def _get_link_data(self, link: GaConditionLink) -> dict:
        """Will get the two results of its condition-link members.
        :param link: Condition link to process
        :type link: GaConditionLink
        :return: Member results
        :rtype: dict
        """
        device_log(f"Getting data for link \"{link.name}\"", add=self.name, level=9)

        result_dict = {}

        # process all conditions in link
        for order, condition in link.condition_match_dict.items():
            if condition.data is not None:
                # get its data from a previous link-result if it is set
                result_dict[order] = condition.data
            else:
                # else process the condition
                result_dict[order] = ConditionResult(condition=condition, device=self.group.name).get()

        for order, condition in link.condition_group_dict.items():
            # if group -> run function recursively
            result_dict[order] = self._process_links(group=condition)

        device_log(f"Data of condition-link \"{link.name}\": \"{result_dict}\"", add=self.name, level=8)

        return result_dict

    def _get_link_data_result(self, link: GaConditionLink, result_dict: dict) -> bool:
        """Will get the result for a link while using its members results.
        :param link: Condition link to process
        :type link: GaConditionLink
        :param result_dict: Results of the links members
        :type result_dict: dict
        :return: Result of the link
        :rtype: bool
        """
        device_log(f"Getting result of condition-link \"{link.name}\"", add=self.name, level=9)

        try:
            result = self._get_result(
                link=link,
                result_dict=result_dict,
            )

            device_log(f"Result of condition-link \"{link.name}\": \"{result}\"", add=self.name, level=7)
            return result

        except (KeyError, ValueError) as error_msg:
            return self._error(error_exception=error_msg)

    def _get_link_to_process(self, group: GaConditionGroup) -> GaConditionLink:
        """Checks which link should be processed next.
        :param group: Condition to check the links from
        :type group: GaConditionGroup
        :return: Next link to process
        :rtype: GaConditionLink
        """
        slm_list = self._get_single_link_member_list(group=group)

        for link in group.member_list:
            if link.processed is False and slm_list[0] in self._get_member_list(link):

                return link

    def _post_process(self, link: GaConditionLink, result: bool, group: GaConditionGroup, process_nr: int, group_member_count: int) -> None:
        """Check which of the two members will be further processed.
        Updating the value of the link to further process to the links result.
        :param link: Link to check the members from
        :type link: GaConditionLink
        :param result: Result of the link
        :type result: bool
        :param group: Condition to which the link belongs
        :type group: GaConditionGroup
        :param process_nr: The links process number
        :type process_nr: int
        :param group_member_count: Number of links in the group
        :type group_member_count: int
        :rtype: None
        :raises: RuntimeError: There is no condition match to further process
        """
        device_log(f"Post-process of condition \"{group.name}\", link \"{link.name}\", result \"{result}\", process_nr \"{process_nr}\", group_member_count \"{group_member_count}\"", level=9)

        slm_list = self._get_single_link_member_list(group=group)
        nslm = False

        for condition in self._get_member_list(link):
            if nslm:
                # there can only be one member to further process
                break

            if condition not in slm_list:
                # if the condition will be further processed -> update its data to the link result
                device_log(f"Updating data of condition \"{condition.name}\" to result \"{result}\"", add=self.name, level=9)

                condition.data = result
                nslm = True

        if process_nr != group_member_count and not nslm:
            # there is no condition that should be further processed and the link is not the last one
            device_log(f"Link \"{link.name}\" (id \"{link.object_id}\") has only single members \"{slm_list}\" and is not the last one to process", add=self.name, level=4)
            self._error(RuntimeError(f"Link with id \"{link.object_id}\" is not the last to process but it does not have any link-neighbors."))

    def _get_single_link_member_list(self, group: GaConditionGroup) -> list:
        """Will get a list of link members that are only linked at one non-processed link.
        We must always start processing at a 'edge' link. Else we might break the chain.
        :param group: Condition to check the link from
        :type group: GaConditionGroup
        :return: List of link members that are linked only once
        :rtype: list
        """
        device_log(f"Getting single link members for condition \"{group.name}\"", add=self.name, level=9)

        lm_list = []
        slm_list = []

        for link in group.member_list:
            if not link.processed:
                lm_list.extend(self._get_member_list(link))

        # check all non-processed link members for multiple occurrence
        counted = Counter(lm_list)

        for instance, count in counted.items():
            if count == 1:
                slm_list.append(instance)

        device_log(f"Condition \"{group.name}\" has the following single link members \"{slm_list}\"", add=self.name, level=8)

        if len(slm_list) == 0:
            raise ValueError("It looks like you have a configuration error.")

        return slm_list

    def _error(self, error_exception: (KeyError, ValueError, RuntimeError)):
        """Resetting 'flags' before raising the error
        :param error_exception: Exception to raise
        :raises: KeyError, ValueError, RuntimeError
        """
        self._reset_flags(group=self.group)
        raise error_exception

    def _reset_flags(self, group: GaConditionGroup) -> None:
        """Resets states of links and data of link members and resets them to the defaults.
        :param group: Condition to process for resetting
        :type group: GaConditionGroup
        :rtype: None
        """
        device_log(f"Resetting flags for condition \"{group.name}\"", add=self.name, level=9)

        for link in group.member_list:
            link.processed = False
            for condition in self._get_member_list(link):
                condition.data = None

    @staticmethod
    def _get_member_list(link: GaConditionLink) -> list:
        """Joins nested conditions and matches to a member list.
        :param link: Link to get the members from
        :type link: GaConditionLink
        :return: A list of link members.
        :rtype: list
        """
        check_list = list(link.condition_match_dict.values())
        check_list.extend(list(link.condition_group_dict.values()))
        return check_list

    def _get_result(self, result_dict: dict, link: GaConditionLink) -> bool:
        """Calculate the link result from its member results.
        Comparison is done using the link operator.
        :param result_dict: Results of link members
        :type result_dict: dict
        :param link: Link that is currently processed
        :type link: GaConditionLink
        :return: Link result
        :rtype: bool
        """
        if len(result_dict) != 2 or LINK_ORDER_ID_1 not in result_dict or LINK_ORDER_ID_2 not in result_dict:
            device_log(
                f"Condition link \"{link.name}\" (id \"{link.object_id}\") has more or less than 2 results: \"{result_dict}\" => could be a configuration error",
                level=7, add=self.name
            )

            # allowing a link with only one member
            if len(result_dict) == 1:
                return list(result_dict.values())[0]

            raise ValueError(f'Got not acceptable results for members of link \"{link.name}\"')

        op = link.operator
        device_log(f"Processing condition link \"{link.name}\", operator \"{op}\", result dict \"{result_dict}\"", add=self.name, level=7)

        if op == 'and':
            result = all(result_dict.values())

        elif op == 'nand':
            result = not all(result_dict.values())

        elif op == 'or':
            result = any(result_dict.values())

        elif op == 'nor':
            result = not any(result_dict.values())

        elif op == 'not':
            result = True if result_dict[LINK_ORDER_ID_1] is True and result_dict[LINK_ORDER_ID_2] is False else False

        elif op == 'xor':
            result = result_dict[LINK_ORDER_ID_1] != result_dict[LINK_ORDER_ID_2]

        elif op == 'xnor':
            result = not (result_dict[LINK_ORDER_ID_1] != result_dict[LINK_ORDER_ID_2])

        else:
            device_log(f"Condition link \"{link.name}\" (id \"{link.object_id}\") has an unsupported operator '{op}", add=self.name, level=3)
            raise ValueError(f"Unsupported operator for link \"{link.name}\"")

        return result

    def __del__(self):
        self._reset_flags(self.group)
