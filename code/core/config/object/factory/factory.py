# is dynamically generating all the objects used throughout the ga-core
# gets the prepared data from the supply module

from core.config.object.factory.supply import Go as GetDataDictTuple
from core.config.object.factory.blueprint import Go as GetBlueprint
from core.config.object.factory.supply import SUPPLY_DICT


class Go:
    def __init__(self):
        self.OBJECT_DICT, self.GROUP_DICT, self.GROUPTYPE_DICT = GetDataDictTuple().get()
        # print("object dict:\n", self.OBJECT_DICT)
        # print("group dict:\n", self.GROUP_DICT)
        # print("grouptype dict:\n", self.GROUPTYPE_DICT)

        self.blueprint_dict = GetBlueprint(type_dict=self.GROUPTYPE_DICT).get()
        # print(self.blueprint_dict)

        self.object_dict = {}

    def get(self) -> dict:
        self._forge_instance_group()
        print(self.object_dict)
        return self.object_dict

    def _forge_instance_object(self, oid: int, type_id: int, model_instance):
        config_dict = self.OBJECT_DICT[oid]

        blueprint = self.blueprint_dict[type_id]['object']

        instance = blueprint(
            setting_dict=config_dict['setting_dict'],
            name=config_dict['ObjectName'],
            description=config_dict['ObjectDescription'],
            object_id=oid,
            model_instance=model_instance
        )

        if 'object' in self.object_dict:
            self.object_dict['object'].append(instance)
        else:
            self.object_dict['object'] = [instance]

        return instance

    def _forge_instance_group(self) -> None:
        for gid, config_dict in self.GROUP_DICT.items():
            blueprint = self.blueprint_dict[config_dict[SUPPLY_DICT['group']['type_id_key']]]['model']

            member_instance_list = []

            instance = blueprint(
                parent=config_dict['GroupParent'],
                type_id=int(config_dict['GroupTypeID']),
                member_list=member_instance_list,
                setting_dict=config_dict['setting_dict'],
                name=config_dict['GroupName'],
                description=config_dict['GroupDescription'],
                object_id=int(gid)
            )

            instance.member_list = self._create_member_list(config_dict=config_dict, instance=instance)

            if 'group' in self.object_dict:
                self.object_dict['group'].append(instance)
            else:
                self.object_dict['group'] = [instance]

    def _create_member_list(self, config_dict: dict, instance) -> list:
        # creates member list with instances of children in it
        member_instance_list = []

        def _create_object():
            member_instance_list.append(
                self._forge_instance_object(
                    oid=int(member_id),
                    type_id=int(config_dict['GroupTypeID']),
                    model_instance=instance
                ))
            # only a group knows its type-id
            # to choose a blueprint the type-id is needed

        for member_id in config_dict['member_list']:
            if 'object' in self.object_dict:
                instance_exists = False

                # check if it already exists
                for obj in self.object_dict['object']:
                    if obj.object_id == member_id:
                        instance_exists = True
                        member_instance_list.append(obj)
                        break

                # or create it
                if not instance_exists:
                    _create_object()
            # or create it
            else:
                _create_object()

        return member_instance_list


if __name__ == '__main__':
    Go().get()
