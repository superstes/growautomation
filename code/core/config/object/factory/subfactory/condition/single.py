# creates instances for single-conditions

from core.utils.debug import debugger
from core.config.object.factory.supply import SUPPLY_DICT
from core.config.object.factory.helper import factory as helper


SINGLE_KEY = helper.FACTORY_CONDITION_SINGLE_KEY


def go(self) -> None:
    # creates instances of objects defined as 'helper.FACTORY_CONDITION_SINGLE_KEY' in the blueprint

    blueprint = self.blueprint_dict[self.type_id][helper.BLUEPRINT_OBJECT_KEY]

    name_key = SUPPLY_DICT[SINGLE_KEY]['name_key']
    description_key = SUPPLY_DICT[SINGLE_KEY]['description_key']
    object_key = SUPPLY_DICT[SINGLE_KEY]['object_key']

    # get instance of object linked to
    for oid, config_dict in self.condition_data_dict.items():
        for instance in self.existing_object_dict[helper.FACTORY_OBJECT_KEY]:
            if instance.object_id == config_dict[object_key]:
                object_instance = instance
                break

        debugger("config-obj-factory-condition-single | go | creating condition '%s' linked to object '%s'"
                 % (config_dict[name_key], object_instance.name))

        instance = blueprint(
            name=config_dict[name_key],
            description=config_dict[description_key],
            setting_dict=config_dict[self.SETTING_KEY],
            check_instance=object_instance,
            object_id=oid
        )

        self.object_dict = helper.add_instance(
            object_dict=self.object_dict,
            obj_type=SINGLE_KEY,
            instance=instance
        )
