# creates default object instances

from core.utils.debug import debugger
from core.config.object.factory.supply import SUPPLY_DICT
from core.config.object.factory.helper import factory as helper
from core.config.object.factory.subfactory.condition_link import Go as ConditionLink


class Go:
    GROUP_KEY = helper.FACTORY_CONDITION_GROUP_KEY
    LINK_KEY = helper.FACTORY_CONDITION_LINK_KEY
    SINGLE_KEY = helper.FACTORY_CONDITION_SINGLE_KEY

    GROUP_TYPEID_KEY = SUPPLY_DICT[GROUP_KEY]['type_id_key']
    SETTING_KEY = helper.FACTORY_SETTING_KEY
    MEMBER_KEY = helper.FACTORY_CONDITION_MEMBER_KEY

    GROUP_MEMBER_SUBKEY = helper.SUPPLY_MEMBER_CONDITION_GROUP_SUBLIST[0]
    GROUP_MEMBER_OUTPUT_SUBKEY = helper.SUPPLY_MEMBER_CONDITION_GROUP_SUBLIST[1]

    def __init__(self, condition_dict: dict, condition_group_dict: dict, condition_link_dict: dict,
                 blueprint_dict: dict, object_dict: dict):
        self.condition_data_dict = condition_dict
        self.condition_group_data_dict = condition_group_dict
        self.condition_link_data_dict = condition_link_dict
        self.blueprint_dict = blueprint_dict
        self.existing_object_dict = object_dict
        self.object_dict = {}
        self.type_id = [config[self.GROUP_TYPEID_KEY] for config in condition_group_dict.values()][0]

    def get(self):
        # {
        #     condition: [instance_list],
        #     condition_group: [instance_list],
        #     condition_link: [instance_list]
        # }

        self._forge_condition()
        self._forge_condition_group()

        # adding members to groups
        self._add_members()

        # adding members to links
        self.object_dict = ConditionLink(
                object_dict=self.object_dict,
                link_data_dict=self.condition_link_data_dict,
                blueprint_dict=self.blueprint_dict[self.type_id]
            ).add_members()

        return self.object_dict

    def _forge_condition(self) -> None:
        # creates instances of objects defined as 'helper.FACTORY_CONDITION_SINGLE_KEY' in the blueprint

        blueprint = self.blueprint_dict[self.type_id][helper.BLUEPRINT_OBJECT_KEY]

        name_key = SUPPLY_DICT[self.SINGLE_KEY]['name_key']
        description_key = SUPPLY_DICT[self.SINGLE_KEY]['description_key']
        object_key = SUPPLY_DICT[self.SINGLE_KEY]['object_key']

        # get instance of object linked to
        for oid, config_dict in self.condition_data_dict.items():
            for instance in self.existing_object_dict[helper.FACTORY_OBJECT_KEY]:
                if instance.name == config_dict[object_key]:
                    object_instance = instance
                    break

            debugger("config-obj-factory-condition | _forge_condition | creating condition '%s' linked to object '%s'"
                     % (config_dict[name_key], object_instance.name))

            instance = blueprint(
                name=config_dict[name_key],
                description=config_dict[description_key],
                config_dict=config_dict[self.SETTING_KEY],
                check_instance=object_instance,
                object_id=oid
            )

            self.object_dict = helper.add_instance(
                object_dict=self.object_dict,
                obj_type=self.SINGLE_KEY,
                instance=instance
            )

    def _forge_condition_group(self):
        # creates instances of objects defined as 'helper.FACTORY_CONDITION_GROUP_KEY' in the blueprint

        name_key = SUPPLY_DICT[self.GROUP_KEY]['name_key']
        description_key = SUPPLY_DICT[self.GROUP_KEY]['description_key']
        parent_key = SUPPLY_DICT[self.GROUP_KEY]['parent_key']

        for gid, config_dict in self.condition_group_data_dict.items():
            debugger("config-obj-factory-condition | _forge_condition_group | forging instance '%s'" % config_dict)

            try:
                blueprint = self.blueprint_dict[self.type_id][helper.BLUEPRINT_GROUP_KEY]
            except KeyError as error_msg:
                # log error or whatever (typeid not found)
                raise KeyError("No blueprint found for type '%s'. Error: '%s'" %
                               (config_dict[self.GROUP_TYPEID_KEY], error_msg))

            instance = blueprint(
                parent=config_dict[parent_key],
                type_id=int(config_dict[self.GROUP_TYPEID_KEY]),
                member_list=[],
                output_list=[],
                name=config_dict[name_key],
                description=config_dict[description_key],
                object_id=int(gid),
                setting_dict=config_dict[self.SETTING_KEY]
            )

            self.object_dict = helper.add_instance(
                object_dict=self.object_dict,
                obj_type=self.GROUP_KEY,
                instance=instance
            )

    def _add_members(self):
        # NOTE:
        # condition_group_data_dict
        #   {
        #     ObjectId :
        #       {
        #          member_dict: {
        #              subkey1: {
        #                  links: [list],
        #                  conditiongroups: [list]
        #              },
        #              subkey2: {
        #                  objects: [list],
        #                  groups: [list]
        #              },
        #          }
        #          setting_dict: {  -> only if the type has settings
        #              setting1: value1,
        #              setting2: value2
        #          }
        #       }
        #   }

        for gid, config_dict in self.condition_group_data_dict.items():
            instance = [inst for inst in self.object_dict[self.GROUP_KEY] if inst.object_id == int(gid)][0]

            for sub_key, sub_config_dict in config_dict[self.MEMBER_KEY].items():
                for key, value_list in sub_config_dict.items():
                    for value in value_list:
                        if sub_key == self.GROUP_MEMBER_SUBKEY:
                            # check all members in member list and link their existing instances
                            if key == self.LINK_KEY:
                                member = self._check_link_member(link_id=int(value))

                                if member is None:
                                    # log error or whatever
                                    continue

                                instance.member_list.append(member)
                            elif key == self.GROUP_KEY:
                                member = self._check_group_member(gid=int(value))

                                if member is None:
                                    # log error or whatever
                                    continue

                                instance.member_list.append(member)

                            else:
                                # log error or whatever
                                pass

                        elif sub_key == self.GROUP_MEMBER_OUTPUT_SUBKEY:
                            # check all members in output list and link their existing instances
                            for category, obj in self.existing_object_dict.items():
                                found = False

                                if category == key and obj.object_id == int(value):
                                    instance.output_list.append(obj)
                                    found = True

                                if not found:
                                    # log error or whatever
                                    pass

                        else:
                            # log error or whatever
                            pass

            # creates member list for condition-groups with instances of those in it
            # sub-groups are not a member of groups; they are members of links

            debugger("config-obj-factory-condition | _create_member_list | creating member list for instance '%s'"
                     % instance)

    def _check_link_member(self, link_id: int):
        member = None
        instance_exists = False

        # check if it already exists
        if self.LINK_KEY in self.object_dict:
            for obj in self.object_dict[self.LINK_KEY]:
                if obj.object_id == link_id:
                    member = obj
                    instance_exists = True
                    break

        # or create it
        if not instance_exists:
            new_instance = (
                ConditionLink(
                    object_dict=self.object_dict,
                    link_data_dict=self.condition_link_data_dict,
                    blueprint_dict=self.blueprint_dict[self.type_id]
                ).get(link_id=link_id)
            )

            member = new_instance

        return member

    def _check_group_member(self, gid: int):
        member = None

        # find and link it
        for obj in self.object_dict[self.GROUP_KEY]:
            if obj.object_id == gid:
                member = obj
                break

        return member
