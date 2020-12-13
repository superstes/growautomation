# creates default object instances

from core.factory import config
from core.factory.forge.blueprint import blueprint_dict
from core.factory.forge.condition.link import Go as ConditionLink
from core.factory.forge.condition.match import Go as ConditionMatch
from core.factory.forge.condition.group import Go as ConditionGroup
from core.factory.forge.member import Go as Member


class Go:
    def __init__(self, factory_dict: dict, supply_dict: dict):
        self.factory_dict = factory_dict
        self.supply_dict = supply_dict

        self.key_condition_match = config.KEY_OBJECT_CONDITION_MATCH
        self.key_condition_link = config.KEY_OBJECT_CONDITION_LINK
        self.key_condition_group = config.KEY_GROUP_CONDITION

        self.member_attribute = config.CORE_MEMBER_ATTRIBUTE

    def get(self) -> dict:
        # {
        #     object_condition_match: [instance_list],
        #     object_condition_link: [instance_list],
        #     group_condition: [instance_list]
        # }

        output_dict = {
            self.key_condition_match: ConditionMatch(
                blueprint=blueprint_dict[self.key_condition_match],
                supply_list=self.supply_dict[self.key_condition_match],
                input_object_dict={
                    config.KEY_OBJECT_INPUT: self.factory_dict[config.KEY_OBJECT_INPUT],
                    config.KEY_GROUP_INPUT: self.factory_dict[config.KEY_GROUP_INPUT],
                }
            ).get()
        }

        condition_link_list = ConditionLink(
            blueprint=blueprint_dict[self.key_condition_link],
            supply_list=self.supply_dict[self.key_condition_link],
        ).get()

        condition_group_list = ConditionGroup(
            blueprint=blueprint_dict[self.key_condition_group],
            supply_list=self.supply_dict[self.key_condition_group],
        ).get()

        condition_link_list = Member(
            object_list=condition_link_list,
            member_list=output_dict[self.key_condition_match],
            member_attribute='condition_match_dict',
            member_typ=config.SUPPLY_CL_KEY_MEMBER_CM
        ).add()

        condition_link_list = Member(
            object_list=condition_link_list,
            member_list=condition_group_list,
            member_attribute='condition_group_dict',
            member_typ=config.SUPPLY_CL_KEY_MEMBER_CG
        ).add()

        condition_group_list = Member(
            object_list=condition_group_list,
            member_list=self.factory_dict[config.KEY_OBJECT_OUTPUT],
            member_attribute='output_object_list',
        ).add()

        condition_group_list = Member(
            object_list=condition_group_list,
            member_list=self.factory_dict[config.KEY_GROUP_OUTPUT],
            member_attribute='output_group_list',
        ).add()

        condition_group_list = Member(
            object_list=condition_group_list,
            member_list=condition_link_list,
            member_attribute=self.member_attribute,
        ).add()

        output_dict[self.key_condition_group] = condition_group_list
        output_dict[self.key_condition_link] = condition_link_list

        return output_dict

