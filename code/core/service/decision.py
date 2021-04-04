# checks thread instance for which submodule to execute

from core.config.object.device.input import GaInputDevice
from core.config.object.device.input import GaInputModel
from core.config.object.core.task import GaTaskDevice
from core.config.object.setting.condition import GaConditionGroup

from core.utils.debug import Log


class Go:
    def __init__(self, instance):
        self.instance = instance
        self.logger = Log()

    def start(self):
        if isinstance(self.instance, (GaInputDevice, GaInputModel)):
            self._device_input()

        elif isinstance(self.instance, GaConditionGroup):
            self._device_output()

        elif isinstance(self.instance, GaTaskDevice):
            self._core_timer()

        else:
            self.logger.write(f"Service could not find a matching decision for instance: '{self.instance}'", level=5)

    def _device_input(self):
        from core.device.input.main import Go
        Go(instance=self.instance).start()

    def _device_output(self):
        from core.device.output.main import Go
        Go(instance=self.instance).start()

    def _core_timer(self):
        self.logger.write('Core timers are not yet implemented', level=3)
        pass
