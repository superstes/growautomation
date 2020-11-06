# is dynamically generating all the objects used throughout the ga-core
# gets the prepared data from the supply module

from core.utils.debug import debugger
from core.config.object.factory.supply import Go as Supply
from core.config.object.factory.blueprint import Go as Blueprint
from core.config.object.factory.subfactory.default import Go as DefaultFactory
from core.config.object.factory.subfactory.condition import Go as ConditionFactory
from core.config.object.factory.helper import factory as helper


class Go:
    def __init__(self):
        self.data_dict = Supply().get()
        self.blueprint_dict = Blueprint(type_dict=self.data_dict[helper.SUPPLY_GROUPTYPE_KEY]).get()

    def get(self) -> tuple:
        debugger("config-obj-factory | get | blueprint dict '%s'" % self.blueprint_dict)

        default_object_dict = DefaultFactory(
            group_dict=self.data_dict[helper.FACTORY_GROUP_KEY],
            object_dict=self.data_dict[helper.FACTORY_OBJECT_KEY],
            blueprint_dict=self.blueprint_dict
        ).get()

        condition_object_dict = ConditionFactory(
            condition_dict=self.data_dict[helper.FACTORY_CONDITION_SINGLE_KEY],
            condition_group_dict=self.data_dict[helper.FACTORY_CONDITION_GROUP_KEY],
            condition_link_dict=self.data_dict[helper.FACTORY_CONDITION_LINK_KEY],
            blueprint_dict=self.blueprint_dict,
            object_dict=default_object_dict
        ).get()

        print(condition_object_dict)

        object_dict = {**condition_object_dict, **default_object_dict}

        debugger("config-obj-factory | get | object dict '%s'" % object_dict)

        return object_dict, self.data_dict
