# creates default object instances

from core.utils.debug import debugger
from core.config.object.factory.supply import SUPPLY_DICT
from core.config.object.factory.helper import factory as helper
from core.config.object.factory.subfactory.condition_link import Go as ConditionLink


class Go:
    GROUP_TYPEID_KEY = SUPPLY_DICT[helper.FACTORY_CONDITION_GROUP_KEY]['type_id_key']

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
        self._create_group_filter()
        self.object_dict = ConditionLink(
                object_dict=self.object_dict,
                group_data_dict=self.condition_group_data_dict,
                link_data_dict=self.condition_link_data_dict,
                type_id=self.type_id,
                blueprint_dict=self.blueprint_dict
            ).add_members()

        return self.object_dict

    def _forge_condition(self) -> None:
        # creates instances of objects defined as 'helper.FACTORY_CONDITION_SINGLE_KEY' in the blueprint

        obj_type = helper.FACTORY_CONDITION_SINGLE_KEY
        blueprint = self.blueprint_dict[self.type_id][helper.BLUEPRINT_OBJECT_KEY]

        name_key = SUPPLY_DICT[obj_type]['name_key']
        description_key = SUPPLY_DICT[obj_type]['description_key']
        operator_key = SUPPLY_DICT[obj_type]['operator_key']
        value_key = SUPPLY_DICT[obj_type]['value_key']
        period_key = SUPPLY_DICT[obj_type]['period_key']
        object_key = SUPPLY_DICT[obj_type]['object_key']

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
                operator=config_dict[operator_key],
                value=config_dict[value_key],
                period=config_dict[period_key],
                check_instance=object_instance,
                object_id=oid
            )

            self.object_dict = helper.add_instance(
                object_dict=self.object_dict,
                obj_type=obj_type,
                instance=instance
            )

    def _create_group_filter(self):
        parent_key = SUPPLY_DICT['condition_group']['parent_key']

        for gid, config_dict in self.condition_group_data_dict.items():
            if config_dict[parent_key] is not None:
                # groups which are children of other groups will be created via '_create_member_list'
                continue
            else:
                self._forge_condition_group(gid=gid, config_dict=config_dict)

    def _forge_condition_group(self, gid, config_dict: dict):
        # creates instances of objects defined as 'helper.FACTORY_CONDITION_GROUP_KEY' in the blueprint

        obj_type = helper.FACTORY_CONDITION_GROUP_KEY

        name_key = SUPPLY_DICT[obj_type]['name_key']
        description_key = SUPPLY_DICT[obj_type]['description_key']
        parent_key = SUPPLY_DICT[obj_type]['parent_key']

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
            name=config_dict[name_key],
            description=config_dict[description_key],
            object_id=int(gid),
            setting_dict=config_dict[helper.FACTORY_SETTING_KEY]
        )

        instance.member_list = self._create_member_list(instance=instance)

        self.object_dict = helper.add_instance(
            object_dict=self.object_dict,
            obj_type=obj_type,
            instance=instance
        )

        return instance

    def _create_member_list(self, instance) -> list:
        # creates member list for condition-groups with instances of those in it

        debugger("config-obj-factory-condition | _create_member_list | creating member list for instance '%s'"
                 % instance)
        member_instance_list = []

        # sub-groups are not a member of groups; they are members of links
        # member_instance_list.extend(
        #     self._create_member_group(
        #         instance=instance
        #     )
        # )

        member_instance_list.extend(
            ConditionLink(
                object_dict=self.object_dict,
                group_data_dict=self.condition_group_data_dict,
                link_data_dict=self.condition_link_data_dict,
                type_id=self.type_id,
                blueprint_dict=self.blueprint_dict
            ).get()
        )

        return member_instance_list

    def _create_member_group(self, instance):
        obj_type = helper.FACTORY_CONDITION_GROUP_KEY
        linked_key = SUPPLY_DICT[obj_type]['parent_key']
        member_group = []

        for gid, config_dict in self.condition_group_data_dict.items():
            instance_exists = False

            parent_id = config_dict[linked_key]
            if parent_id is None:
                continue

            if int(parent_id) == instance.object_id:

                if obj_type in self.object_dict:
                    for obj in self.object_dict[obj_type]:
                        # check if it already exists
                        if obj.object_id == int(gid):
                            member_group.append(obj)
                            instance_exists = True
                            break

                if not instance_exists:
                    # or create it
                    new_instance = self._forge_condition_group(gid=gid, config_dict=config_dict)
                    member_group.append(new_instance)

        return member_group
