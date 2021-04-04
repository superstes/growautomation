from core.factory.supply.main import Go as Supply
from core.factory.forge.condition.main import Go as ConditionFactory
from core.factory.forge.group.main import Go as GroupFactory
from core.factory.forge.device.main import Go as DeviceFactory
from core.factory.forge.system.main import Go as SystemFactory
from core.factory.link.main import Go as CreateLinks
from core.utils.debug import Log

logger = Log()


def _log_parse(prefix: str, output: dict, level: int) -> None:
    for _key, _list in output.items():
        logger.write(f'{prefix} output (detailed): \"{_key}\" => \"{[instance.__dict__ for instance in _list]}\"', level=level)


def get() -> tuple:
    """
    Calls sub-factories to create all needed objects
    :return:
    """
    supply_data = Supply().get()
    logger.write(f'Supply data: \"{supply_data}\"', level=7)

    _config = {
        'device': DeviceFactory,
        'group': GroupFactory,
        'condition': ConditionFactory,
        'system': SystemFactory,
    }

    factory_data = {}

    for key, factory in _config.items():
        _ = factory(
            supply_data=supply_data,
            factory_data=factory_data,
        ).get()

        factory_data.update(_.copy())

        log_prefix = f'{key.capitalize()} factory'
        logger.write(f'{log_prefix} output: \"{_}\"', level=7)
        _log_parse(prefix=log_prefix, output=_, level=8)

    CreateLinks(
        factory_data=factory_data,
        supply_data=supply_data
    ).set()

    logger.write(f'Factory output: \"{factory_data}\"', level=6)
    _log_parse(prefix='Factory', output=factory_data, level=7)

    return factory_data.copy(), supply_data.copy()
