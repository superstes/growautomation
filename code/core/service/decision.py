# checks thread instance for which submodule to execute

from core.config.object.device.input import GaInputDevice
from core.config.object.device.input import GaInputModel
from core.config.object.core.task import GaTaskDevice, SystemTask
from core.config.object.setting.condition import GaConditionGroup

from core.utils.debug import log


def start(instance, settings: dict = None):
    if settings is None:
        settings = {}

    if isinstance(instance, (GaInputDevice, GaInputModel)):
        from core.device.input.main import Go
        Go(instance=instance, **settings).start()

    elif isinstance(instance, GaConditionGroup):
        from core.device.output.main import Go
        Go(instance=instance, **settings).start()

    elif isinstance(instance, GaTaskDevice):
        log('Core timers are not yet implemented', level=3)
        pass

    elif isinstance(instance, SystemTask):
        instance.execute(**settings)

    else:
        log(f"Service could not find a matching decision for instance: '{instance}'", level=5)
