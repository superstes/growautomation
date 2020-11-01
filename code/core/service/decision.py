# checks thread instance for which submodule to execute

from core.config.object.device.input import GaInputDevice
from core.config.object.device.input import GaInputModel
from core.config.object.core.timer import GaTimerDevice


class Go:
    TIMER_OUTPUT_NAME = 'output-timer'
    TIMER_BACKUP_NAME = 'backup-timer'

    def __init__(self, instance):
        self.instance = instance

    def start(self):
        if isinstance(self.instance, (GaInputDevice, GaInputModel)):
            self._device_input()
        elif isinstance(self.instance, GaTimerDevice):
            self._core_timer()

    def _device_input(self):
        from core.device.input.input import Go
        Go(instance=self.instance).start()

    @staticmethod
    def _device_output():
        from core.device.output.output import Go
        Go().start()

    def _core_timer(self):
        if self.instance.name == self.TIMER_OUTPUT_NAME:
            self._device_output()
        elif self.instance.name == self.TIMER_BACKUP_NAME:
            self._backup()

    def _backup(self):
        pass
