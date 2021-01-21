from core.utils.debug import debugger
from core.factory.supply.main import Go as Supply
from core.factory.forge.condition.main import Go as ConditionFactory
from core.factory.forge.group.main import Go as GroupFactory
from core.factory.forge.device.main import Go as DeviceFactory
from core.factory.forge.system.main import Go as SystemFactory


def get() -> tuple:
    supply_data = Supply().get()

    factory_dict = DeviceFactory(
        supply_dict=supply_data,
    ).get()

    factory_dict.update(
        GroupFactory(
            factory_dict=factory_dict,
            supply_dict=supply_data,
        ).get()
    )

    factory_dict.update(
        ConditionFactory(
            factory_dict=factory_dict,
            supply_dict=supply_data,
        ).get()
    )

    factory_dict.update(
        SystemFactory(
            supply_dict=supply_data,
        ).get()
    )

    debugger("config-obj-factory | get | object dict \"%s\"" % factory_dict)

    return factory_dict, supply_data
