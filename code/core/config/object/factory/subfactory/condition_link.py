# handles creation of condition link instances

from core.utils.debug import debugger
from core.config.object.factory.supply import SUPPLY_DICT
from core.config.object.factory.helper import factory as helper


class Go:
    def __init__(self, object_dict: dict, group_data_dict: dict, blueprint_dict: dict, link_data_dict: dict,
                 type_id: int):
        self.object_dict = object_dict
        self.condition_group_data_dict = group_data_dict
        self.condition_link_data_dict = link_data_dict
        self.type_id = type_id
        self.blueprint_dict = blueprint_dict

    def get(self):
        return self._create_link()

    def _create_link(self):
        # creates condition links to be added as members of condition groups

        obj_type = helper.FACTORY_CONDITION_LINK_KEY
        member_link = []

        for gid, config_dict in self.condition_group_data_dict.items():
            instance_exists = False

            member_list = config_dict[helper.FACTORY_MEMBER_KEY]

            for member in member_list:

                if obj_type in self.object_dict:
                    for obj in self.object_dict[obj_type]:
                        # check if it already exists
                        if obj.object_id == int(member):
                            member_link.append(obj)
                            instance_exists = True
                            break

                if not instance_exists:
                    # or create it
                    new_instance = self._forge_link(linkid=member)
                    member_link.append(new_instance)

        return member_link

    def _forge_link(self, linkid: int):
        # creates instances of objects defined as 'helper.FACTORY_CONDITION_LINK_KEY' in the blueprint

        obj_type = helper.FACTORY_CONDITION_LINK_KEY

        blueprint = self.blueprint_dict[self.type_id][helper.BLUEPRINT_SETTING_KEY]

        member_group_key = SUPPLY_DICT[obj_type]['member_group_key']
        member_condition_key = SUPPLY_DICT[obj_type]['member_condition_key']
        operator_key = SUPPLY_DICT[obj_type]['operator_key']

        member_dict = {}

        for lid, config in self.condition_link_data_dict.items():
            if int(lid) == linkid:
                config_dict = config
                member_dict[member_group_key] = config[helper.FACTORY_CONDITION_MEMBER_KEY][member_group_key]
                member_dict[member_condition_key] = config[helper.FACTORY_CONDITION_MEMBER_KEY][member_condition_key]

        debugger("config-obj-factory-condition | _forge_condition_link | creating condition link with id '%s'" % linkid)

        instance = blueprint(
            member_list=[member_dict],
            operator=config_dict[operator_key],
            object_id=linkid
        )

        self.object_dict = helper.add_instance(
            object_dict=self.object_dict,
            obj_type=obj_type,
            instance=instance
        )

        return instance

    def add_members(self):
        # adds members to condition link

        obj_type = helper.FACTORY_CONDITION_LINK_KEY

        for link in self.object_dict[obj_type]:
            debugger("config-obj-factory-condition | _add_condition_link_member | adding members for link '%s'"
                     % link.object_id)

            member_group_key = SUPPLY_DICT[obj_type]['member_group_key']
            member_condition_key = SUPPLY_DICT[obj_type]['member_condition_key']

            member_dict = link.member_list[0]
            member_group = member_dict[member_group_key]
            member_condition = member_dict[member_condition_key]

            member_instance_list = []

            for member in member_group:
                for obj in self.object_dict[helper.FACTORY_CONDITION_GROUP_KEY]:
                    if obj.name == member:
                        member_instance_list.append(obj)

            for member in member_condition:
                for obj in self.object_dict[helper.FACTORY_CONDITION_SINGLE_KEY]:
                    if obj.name == member:
                        member_instance_list.append(obj)

            if len(member_instance_list) != 2:
                # log error or whatever
                debugger("config-obj-factory-condition | _add_condition_link_member | link with id '%s' has no two "
                         "members; raw dict '%s'" % (link.object_id, member_dict))

        return self.object_dict
