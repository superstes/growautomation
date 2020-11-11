# checks thread instance for which submodule to execute

from core.config.object.device.input import GaInputDevice
from core.config.object.device.input import GaInputModel
from core.config.object.core.timer import GaTimerDevice
from core.config.object.setting.condition import GaConditionGroup


class Go:
    TIMER_BACKUP_NAME = 'backup-timer'

    def __init__(self, instance):
        self.instance = instance

    def start(self):
        if isinstance(self.instance, (GaInputDevice, GaInputModel)):
            self._device_input()
        elif isinstance(self.instance, GaTimerDevice):
            self._core_timer()
        elif isinstance(self.instance, GaConditionGroup):
            self._device_output()

    def _device_input(self):
        from core.device.input.input import Go
        Go(instance=self.instance).start()

    def _device_output(self):
        from core.device.output.output import Go
        Go(instance=self.instance).start()

    def _core_timer(self):
        if self.instance.name == self.TIMER_BACKUP_NAME:
            pass
