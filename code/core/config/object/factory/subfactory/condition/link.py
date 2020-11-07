# handles creation of condition link instances

from core.utils.debug import debugger
from core.config.object.factory.supply import SUPPLY_DICT
from core.config.object.factory.helper import factory as helper


class Go:
    SUPPLY_SETTING_KEY = helper.SUPPLY_SETTING_KEY
    SUPPLY_MEMBER_KEY = helper.SUPPLY_MEMBER_KEY
    LINK_KEY = helper.FACTORY_CONDITION_LINK_KEY
    SETTING_KEY = helper.FACTORY_SETTING_KEY
    CONDITION_MEMBER_KEY = helper.FACTORY_CONDITION_MEMBER_KEY

    MEMBER_KEY = helper.FACTORY_MEMBER_KEY
    NAME_KEY = SUPPLY_DICT[LINK_KEY]['name_key']
    MEMBER_GROUP_KEY = SUPPLY_DICT[SUPPLY_MEMBER_KEY][LINK_KEY]['member_group_key']
    MEMBER_OBJECT_KEY = SUPPLY_DICT[SUPPLY_MEMBER_KEY][LINK_KEY]['member_object_key']

    def __init__(self, object_dict: dict, blueprint_dict: dict, link_data_dict: dict):
        self.object_dict = object_dict
        self.condition_link_data_dict = link_data_dict
        self.blueprint_dict = blueprint_dict

    def get(self, link_id: int):
        # creates instances of objects defined as 'helper.FACTORY_CONDITION_LINK_KEY' in the blueprint

        blueprint = self.blueprint_dict[helper.BLUEPRINT_SETTING_KEY]

        # member_dict = {}
        for lid, config in self.condition_link_data_dict.items():
            if int(lid) == link_id:
                config_dict = config
        #         member_dict[self.MEMBER_GROUP_KEY] = config[self.CONDITION_MEMBER_KEY][self.MEMBER_GROUP_KEY]
        #
        #         member_dict[self.MEMBER_OBJECT_KEY] = config[self.CONDITION_MEMBER_KEY][self.MEMBER_OBJECT_KEY]

        debugger("config-obj-factory-condition-link | get | creating condition link with id '%s'"
                 % link_id)

        instance = blueprint(
            member_dict=config_dict[self.CONDITION_MEMBER_KEY],
            setting_dict=config_dict[self.SETTING_KEY],
            object_id=link_id,
            name=config_dict[self.NAME_KEY]
        )

        self.object_dict = helper.add_instance(
            object_dict=self.object_dict,
            obj_type=self.LINK_KEY,
            instance=instance
        )

        return instance, self.object_dict

    def add_members(self):
        # adds members to condition link
        # NOTE:
        # condition_link_data_dict
        #   {
        #     ObjectId :
        #       {
        #          member_dict: {
        #              groups: {
        #                  orderid: member
        #              },
        #              objects: {
        #                  orderid: member
        #              },
        #          }
        #          setting_dict: {  -> only if the type has settings
        #              setting1: value1,
        #              setting2: value2
        #          }
        #       }
        #   }

        for link in self.object_dict[self.LINK_KEY]:
            debugger("config-obj-factory-condition-link | get | adding members for link '%s'"
                     % link.object_id)

            member_dict = link.member_dict
            member_group = member_dict[self.MEMBER_GROUP_KEY]
            member_condition = member_dict[self.MEMBER_OBJECT_KEY]

            member_instance_dict = {}

            for order_id, member in member_group.items():
                for obj in self.object_dict[helper.FACTORY_CONDITION_GROUP_KEY]:
                    if obj.object_id == member:
                        member_instance_dict[order_id] = obj

            for order_id, member in member_condition.items():
                for obj in self.object_dict[helper.FACTORY_CONDITION_SINGLE_KEY]:
                    if obj.object_id == member:
                        member_instance_dict[order_id] = obj

            if len(member_instance_dict) != 2:
                # log error or whatever
                debugger("config-obj-factory-condition-link | get | link with id '%s' has no two "
                         "members; raw dict '%s'" % (link.object_id, member_dict))
            else:
                link.member_dict = member_instance_dict

        return self.object_dict
