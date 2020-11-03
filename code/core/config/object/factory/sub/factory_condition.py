# creates default object instances

from core.utils.debug import debugger
from core.config.object.factory.supply import SUPPLY_DICT


class Go:
    GROUP_TYPEID_KEY = SUPPLY_DICT['condition_group']['type_id_key']

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

        parent_key = SUPPLY_DICT['condition_group']['parent_key']

        for gid, config_dict in self.condition_group_data_dict.items():
            if config_dict[parent_key] is not None:
                # groups which are children of other groups will be created via '_create_member_list'
                continue
            else:
                self._forge_condition_group(gid=gid, config_dict=config_dict)

        self._add_condition_link_member()

        return self.object_dict

    def _forge_condition(self) -> None:
        obj_type = 'condition'

        for oid, config_dict in self.condition_data_dict.items():
            blueprint = self.blueprint_dict[self.type_id]['object']

            name_key = SUPPLY_DICT[obj_type]['name_key']
            description_key = SUPPLY_DICT[obj_type]['description_key']
            operator_key = SUPPLY_DICT[obj_type]['operator_key']
            value_key = SUPPLY_DICT[obj_type]['value_key']
            period_key = SUPPLY_DICT[obj_type]['period_key']
            object_key = SUPPLY_DICT[obj_type]['object_key']

            for instance in self.existing_object_dict['object']:
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

            if obj_type in self.object_dict:
                self.object_dict[obj_type].append(instance)
            else:
                self.object_dict[obj_type] = [instance]

    def _forge_condition_group(self, gid, config_dict: dict):
        obj_type = 'condition_group'

        name_key = SUPPLY_DICT[obj_type]['name_key']
        description_key = SUPPLY_DICT[obj_type]['description_key']
        parent_key = SUPPLY_DICT[obj_type]['parent_key']

        debugger("config-obj-factory-condition | _forge_condition_group | forging instance '%s'" % config_dict)

        try:
            blueprint = self.blueprint_dict[self.type_id]['model']
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
            setting_dict=config_dict['setting_dict']
        )

        instance.member_list = self._create_member_list(instance=instance)

        if obj_type in self.object_dict:
            self.object_dict[obj_type].append(instance)
        else:
            self.object_dict[obj_type] = [instance]

        return instance

    def _create_member_group(self, instance):
        obj_type = 'condition_group'
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

    def _create_member_link(self):
        obj_type = 'condition_link'
        member_link = []

        for gid, config_dict in self.condition_group_data_dict.items():
            instance_exists = False

            member_list = config_dict['member_list']

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
                    new_instance = self._forge_condition_link(linkid=member)
                    member_link.append(new_instance)

        return member_link

    def _create_member_list(self, instance) -> list:
        # creates member list with instances of children in it
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
            self._create_member_link()
        )

        return member_instance_list

    def _forge_condition_link(self, linkid: int):
        obj_type = 'condition_link'

        blueprint = self.blueprint_dict[self.type_id]['setting']

        member_group_key = SUPPLY_DICT[obj_type]['member_group_key']
        member_condition_key = SUPPLY_DICT[obj_type]['member_condition_key']
        operator_key = SUPPLY_DICT[obj_type]['operator_key']

        member_dict = {}

        for lid, config in self.condition_link_data_dict.items():
            if int(lid) == linkid:
                config_dict = config
                member_dict[member_group_key] = config['member_dict'][member_group_key]
                member_dict[member_condition_key] = config['member_dict'][member_condition_key]

        debugger("config-obj-factory-condition | _forge_condition_link | creating condition link with id '%s'" % linkid)

        instance = blueprint(
            member_list=[member_dict],
            operator=config_dict[operator_key],
            object_id=linkid
        )

        if obj_type in self.object_dict:
            self.object_dict[obj_type].append(instance)
        else:
            self.object_dict[obj_type] = [instance]

        return instance

    def _add_condition_link_member(self):
        obj_type = 'condition_link'

        for link in self.object_dict['condition_link']:
            debugger("config-obj-factory-condition | _add_condition_link_member | adding members for link '%s'"
                     % link.object_id)

            member_group_key = SUPPLY_DICT[obj_type]['member_group_key']
            member_condition_key = SUPPLY_DICT[obj_type]['member_condition_key']

            member_dict = link.member_list[0]
            member_group = member_dict[member_group_key]
            member_condition = member_dict[member_condition_key]

            member_instance_list = []

            for member in member_group:
                for obj in self.object_dict['condition_group']:
                    if obj.name == member:
                        member_instance_list.append(obj)

            for member in member_condition:
                for obj in self.object_dict['condition']:
                    if obj.name == member:
                        member_instance_list.append(obj)

            if len(member_instance_list) != 2:
                # log error or whatever
                debugger("config-obj-factory-condition | _add_condition_link_member | link with id '%s' has no two "
                         "members; raw dict '%s'" % (link.object_id, member_dict))
