# creates default object instances

from core.utils.debug import debugger
from core.config.object.factory.supply import SUPPLY_DICT


class Go:
    GROUP_TYPEID_KEY = SUPPLY_DICT['group']['type_id_key']

    def __init__(self, group_dict: dict, object_dict: dict, blueprint_dict: dict):
        self.group_data_dict = group_dict
        self.object_data_dict = object_dict
        self.blueprint_dict = blueprint_dict
        self.object_dict = {}

    def get(self):
        # {
        #     group: [instance_list],
        #     object: [instance_list]
        # }
        self._forge_instance_group()
        return self.object_dict

    def _forge_instance_object(self, oid: int, type_id: int, parent_instance):
        debugger("config-obj-factory | _forge_instance_object | creating oid %s for instance '%s'"
                 % (oid, parent_instance))
        config_dict = self.object_data_dict[oid]

        blueprint = self.blueprint_dict[type_id]['object']

        setting_dict_key = SUPPLY_DICT['object']['setting_dict_key']
        name_key = SUPPLY_DICT['object']['name_key']
        description_key = SUPPLY_DICT['object']['description_key']

        instance = blueprint(
            setting_dict=config_dict[setting_dict_key],
            name=config_dict[name_key],
            description=config_dict[description_key],
            object_id=oid,
            parent_instance=parent_instance
        )

        if 'object' in self.object_dict:
            self.object_dict['object'].append(instance)
        else:
            self.object_dict['object'] = [instance]

        return instance

    def _forge_instance_group(self) -> None:
        for gid, config_dict in self.group_data_dict.items():
            debugger("config-obj-factory | _forge_instance_group | forging instance '%s'" % config_dict)

            try:
                blueprint = self.blueprint_dict[config_dict[self.GROUP_TYPEID_KEY]]['model']
            except KeyError as error_msg:
                # log error or whatever (typeid not found)
                raise KeyError("No blueprint found for type '%s'. Error: '%s'" %
                               (config_dict[self.GROUP_TYPEID_KEY], error_msg))

            setting_dict_key = SUPPLY_DICT['group']['setting_dict_key']
            name_key = SUPPLY_DICT['group']['name_key']
            description_key = SUPPLY_DICT['group']['description_key']
            parent_key = SUPPLY_DICT['group']['parent_key']

            instance = blueprint(
                parent=config_dict[parent_key],
                type_id=int(config_dict[self.GROUP_TYPEID_KEY]),
                member_list=[],
                setting_dict=config_dict[setting_dict_key],
                name=config_dict[name_key],
                description=config_dict[description_key],
                object_id=int(gid)
            )

            instance.member_list = self._create_member_list(config_dict=config_dict, instance=instance)

            if 'group' in self.object_dict:
                self.object_dict['group'].append(instance)
            else:
                self.object_dict['group'] = [instance]

    def _create_member_list(self, config_dict: dict, instance) -> list:
        # creates member list with instances of children in it
        debugger("config-obj-factory | _create_member_list | creating member list for instance '%s'" % instance)
        member_instance_list = []

        def _create_object():
            member_instance_list.append(
                self._forge_instance_object(
                    oid=int(member_id),
                    type_id=int(config_dict[self.GROUP_TYPEID_KEY]),
                    parent_instance=instance
                ))
            # only a group knows its type-id
            # to choose a blueprint the type-id is needed

        for member_id in config_dict['member_list']:
            instance_exists = False

            if 'object' in self.object_dict:

                for obj in self.object_dict['object']:
                    # check if it already exists
                    if obj.object_id == int(member_id):
                        instance_exists = True
                        member_instance_list.append(obj)
                        break

            if not instance_exists:
                # or create it
                _create_object()

        return member_instance_list
