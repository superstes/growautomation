# creates default object instances

from core.utils.debug import debugger
from core.config.object.factory.supply import SUPPLY_DICT
from core.config.object.factory.helper import factory as helper
from core.config.object.factory.subfactory.condition.link import Go as ConditionLink
from core.config.object.factory.subfactory.condition.single import go as ConditionObject
from core.config.object.factory.subfactory.condition.group import Go as ConditionGroup


class Go:
    GROUP_KEY = helper.FACTORY_CONDITION_GROUP_KEY
    GROUP_TYPEID_KEY = SUPPLY_DICT[GROUP_KEY]['type_id_key']
    SETTING_KEY = helper.FACTORY_SETTING_KEY

    def __init__(self, condition_dict: dict, condition_group_dict: dict, condition_link_dict: dict,
                 blueprint_dict: dict, object_dict: dict):
        self.condition_data_dict = condition_dict
        self.condition_group_data_dict = condition_group_dict
        self.condition_link_data_dict = condition_link_dict
        self.blueprint_dict = blueprint_dict
        self.existing_object_dict = object_dict
        self.object_dict = {}
        self.type_id = None

    def get(self):
        # {
        #     condition: [instance_list],
        #     condition_group: [instance_list],
        #     condition_link: [instance_list]
        # }

        # find condition type id for factory to use
        for config in self.condition_group_data_dict.values():
            type_id = config[self.GROUP_TYPEID_KEY]
            blueprint = self.blueprint_dict[type_id][helper.BLUEPRINT_GROUP_KEY]

            if blueprint in helper.CUSTOM_CONDITION_BLUEPRINT_LIST:
                self.type_id = type_id
                break

        if self.type_id is None:
            # log error or whatever
            raise SystemExit('Condition type id not found! Cannot proceed with factory')

        ConditionObject(self=self)
        ConditionGroup(parent=self).get()

        # adding members to groups
        ConditionGroup(parent=self).add_members()

        # adding members to links
        self.object_dict = ConditionLink(
                object_dict=self.object_dict,
                link_data_dict=self.condition_link_data_dict,
                blueprint_dict=self.blueprint_dict[self.type_id]
            ).add_members()

        return self.object_dict

