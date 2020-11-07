# creates default object instances

from core.utils.debug import debugger
from core.config.object.factory.supply import SUPPLY_DICT
from core.config.object.factory.helper import factory as helper


class Go:
    GROUP_TYPEID_KEY = SUPPLY_DICT['group']['type_id_key']
    SETTING_KEY = helper.FACTORY_SETTING_KEY

    OBJECT_KEY = helper.FACTORY_OBJECT_KEY
    GROUP_KEY = helper.FACTORY_GROUP_KEY

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
        self._group()
        return self.object_dict

    def _group(self):
        # creates instances of objects defined as 'group' in the blueprint

        for gid, config_dict in self.group_data_dict.items():
            debugger("config-obj-factory-default | _group | forging instance '%s'" % config_dict)

            name_key = SUPPLY_DICT[self.GROUP_KEY]['name_key']
            description_key = SUPPLY_DICT[self.GROUP_KEY]['description_key']
            parent_key = SUPPLY_DICT[self.GROUP_KEY]['parent_key']

            try:
                blueprint = self.blueprint_dict[config_dict[self.GROUP_TYPEID_KEY]][helper.BLUEPRINT_GROUP_KEY]

                if blueprint in helper.CUSTOM_BLUEPRINT_LIST:
                    # if there is a custom factory for the object -> it should not be handled by this one
                    debugger("config-obj-factory-default | _group | skipping group '%s' with id '%s' because "
                             "it is marked as custom" % (config_dict[name_key], gid))
                    continue

            except KeyError as error_msg:
                # log error or whatever (typeid not found)
                raise KeyError("No blueprint found for type '%s'. Error: '%s'" %
                               (config_dict[self.GROUP_TYPEID_KEY], error_msg))

            instance = blueprint(
                parent=config_dict[parent_key],
                type_id=int(config_dict[self.GROUP_TYPEID_KEY]),
                member_list=[],
                setting_dict=config_dict[self.SETTING_KEY],
                name=config_dict[name_key],
                description=config_dict[description_key],
                object_id=int(gid)
            )

            instance.member_list = self._member(config_dict=config_dict, instance=instance)

            self.object_dict = helper.add_instance(
                object_dict=self.object_dict,
                obj_type=self.GROUP_KEY,
                instance=instance
            )

    def _member(self, config_dict: dict, instance) -> list:
        # creates member list with instances of children in it
        debugger("config-obj-factory-default | _member | creating member list for instance '%s'" % instance.name)
        member_instance_list = []

        def _create_object():
            member_instance_list.append(
                self._object(
                    oid=int(member_id),
                    type_id=int(config_dict[self.GROUP_TYPEID_KEY]),
                    parent_instance=instance
                ))
            # only a group knows its type-id
            # to choose a blueprint the type-id is needed

        for member_id in config_dict[helper.FACTORY_MEMBER_KEY]:
            instance_exists = False

            if helper.FACTORY_OBJECT_KEY in self.object_dict:

                for obj in self.object_dict[helper.FACTORY_OBJECT_KEY]:
                    # check if it already exists
                    if obj.object_id == int(member_id):

                        instance_exists = True
                        member_instance_list.append(obj)
                        break

            if not instance_exists:
                debugger("config-obj-factory-default | _create_object | creating member with id '%s' for parent '%s'"
                         % (member_id, instance.name))
                # or create it
                _create_object()

        return member_instance_list

    def _object(self, oid: int, type_id: int, parent_instance):
        # creates instances of objects defined as 'object' in the blueprint

        debugger("config-obj-factory-default | _object | creating oid %s for instance '%s'"
                 % (oid, parent_instance))

        config_dict = self.object_data_dict[oid]
        blueprint = self.blueprint_dict[type_id][helper.BLUEPRINT_OBJECT_KEY]

        name_key = SUPPLY_DICT[self.OBJECT_KEY]['name_key']
        description_key = SUPPLY_DICT[self.OBJECT_KEY]['description_key']

        instance = blueprint(
            setting_dict=config_dict[self.SETTING_KEY],
            name=config_dict[name_key],
            description=config_dict[description_key],
            object_id=oid,
            parent_instance=parent_instance
        )

        self.object_dict = helper.add_instance(
            object_dict=self.object_dict,
            obj_type=self.OBJECT_KEY,
            instance=instance
        )

        return instance
