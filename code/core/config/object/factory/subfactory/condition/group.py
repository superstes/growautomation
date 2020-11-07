# creates condition group instances

from core.utils.debug import debugger
from core.config.object.factory.supply import SUPPLY_DICT
from core.config.object.factory.helper import factory as helper
from core.config.object.factory.subfactory.condition.link import Go as ConditionLink


class Go:
    LINK_KEY = helper.FACTORY_CONDITION_LINK_KEY
    GROUP_KEY = helper.FACTORY_CONDITION_GROUP_KEY

    MEMBER_KEY = helper.FACTORY_CONDITION_MEMBER_KEY

    ID_KEY = 'id_key'
    MEMBER_ID_KEY = 'member_key'  # id_key of member dict

    LINK_MEMBER_ID_KEY = SUPPLY_DICT[LINK_KEY][MEMBER_ID_KEY]
    GROUP_MEMBER_ID_KEY = SUPPLY_DICT[GROUP_KEY][MEMBER_ID_KEY]

    GROUP_MEMBER_SUBKEY = helper.SUPPLY_MEMBER_CONDITION_GROUP_SUBLIST[0]
    GROUP_MEMBER_OUTPUT_SUBKEY = helper.SUPPLY_MEMBER_CONDITION_GROUP_SUBLIST[1]
    
    def __init__(self, parent):
        self.parent = parent
    
    def get(self):
        # creates instances of objects defined as 'helper.FACTORY_CONDITION_GROUP_KEY' in the blueprint

        name_key = SUPPLY_DICT[self.parent.GROUP_KEY]['name_key']
        description_key = SUPPLY_DICT[self.parent.GROUP_KEY]['description_key']
        parent_key = SUPPLY_DICT[self.parent.GROUP_KEY]['parent_key']

        for gid, config_dict in self.parent.condition_group_data_dict.items():
            debugger("config-obj-factory-subfactory-condition-group | get | forging instance '%s'" % config_dict)

            try:
                blueprint = self.parent.blueprint_dict[self.parent.type_id][helper.BLUEPRINT_GROUP_KEY]

            except KeyError as error_msg:
                # log error or whatever (typeid not found)
                raise KeyError("No blueprint found for type '%s'. Error: '%s'" %
                               (config_dict[self.parent.GROUP_TYPEID_KEY], error_msg))

            instance = blueprint(
                parent=config_dict[parent_key],
                type_id=int(config_dict[self.parent.GROUP_TYPEID_KEY]),
                member_list=[],
                output_list=[],
                name=config_dict[name_key],
                description=config_dict[description_key],
                object_id=int(gid),
                setting_dict=config_dict[self.parent.SETTING_KEY]
            )

            self.parent.object_dict = helper.add_instance(
                object_dict=self.parent.object_dict,
                obj_type=self.parent.GROUP_KEY,
                instance=instance
            )

    def add_members(self):
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

        # creates member list for condition-groups with instances of those in it
        # sub-groups are not a member of groups; they are members of links

        for gid, config_dict in self.parent.condition_group_data_dict.items():
            found = False
            
            for inst in self.parent.object_dict[self.parent.GROUP_KEY]:
                if inst.object_id == int(gid):
                    instance = inst
                    found = True
                    break
                    
            if not found:
                # log error or whatever
                continue

            for sub_key, sub_config in config_dict[self.MEMBER_KEY].items():
                if sub_key == self.GROUP_MEMBER_OUTPUT_SUBKEY:
                    self._output_list(
                        config=sub_config,
                        instance=instance
                    )
                elif sub_key == self.GROUP_MEMBER_SUBKEY:
                    self._member_list(
                        config=sub_config,
                        instance=instance
                    )

            debugger("config-obj-factory-subfactory-condition-group | add_members | "
                     "members for instance '%s' | output list '%s' | member list '%s'"
                     % (instance.name, instance.output_list, instance.member_list))

    def _output_list(self, config: dict, instance):
        for key, output_list in config.items():
            if len(output_list) == 0:
                continue

            # check all members in output list and link their existing instances
            for category, obj_list in self.parent.existing_object_dict.items():
                category_key = SUPPLY_DICT[category][self.ID_KEY]

                found = False
                if category_key == key:
                    for obj in obj_list:
                        if obj.object_id in output_list:
                            instance.output_list.append(obj)
                            found = True

                if not found:
                    # log error or whatever
                    debugger("config-obj-factory-subfactory-condition-group | _output_list | "
                             "no matching instance for output found - category '%s', cat-compare '%s', output_list '%s'"
                             % (category_key, key, output_list))

    def _member_list(self, config: list, instance):
        # check all members in member list and link their existing instances

        for value in config:
            member = self._check_link_member(link_id=int(value))

            if member is None:
                # log error or whatever
                pass

            instance.member_list.append(member)

    def _check_link_member(self, link_id: int):
        member = None
        instance_exists = False

        # check if it already exists
        if self.LINK_KEY in self.parent.object_dict:
            for obj in self.parent.object_dict[self.LINK_KEY]:
                if obj.object_id == link_id:
                    member = obj
                    instance_exists = True
                    break

        # or create it
        if not instance_exists:
            new_instance, self.parent.object_dict = (
                ConditionLink(
                    object_dict=self.parent.object_dict,
                    link_data_dict=self.parent.condition_link_data_dict,
                    blueprint_dict=self.parent.blueprint_dict[self.parent.type_id]
                ).get(link_id=link_id)
            )

            member = new_instance

        return member

    def _check_group_member(self, gid: int):
        member = None

        # find and link it
        for obj in self.parent.object_dict[self.parent.GROUP_KEY]:
            if obj.object_id == gid:
                member = obj
                break

        return member
