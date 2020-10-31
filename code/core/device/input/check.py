# will check for which input scripts to start
# basic filtering on enabled state and model grouping

from core.config.object.device.input import GaInputModel
from core.config.object.device.input import GaInputDevice
from core.utils.debug import debugger


class Go:
    MODEL_OBJECT = GaInputModel
    DEVICE_OBJECT = GaInputDevice

    def __init__(self, instance):
        self.instance = instance
        self.task_instance_list = []

    def get(self) -> list:
        if isinstance(self.instance, self.MODEL_OBJECT):
            self._model()
        elif isinstance(self.instance, self.DEVICE_OBJECT):
            self._device(instance=self.instance)
        else:
            # log error or whatever
            pass

        debugger("input | check | instance '%s' - instance_list to process: '%s'"
                 % (self.instance.name, self.task_instance_list))

        return self.task_instance_list

    def _model(self):
        for device_instance in self.instance.member_list:
            if device_instance.enabled:
                self._device(instance=device_instance)

    def _device(self, instance):
        print(type(instance.downlink), instance.downlink)
        if instance.downlink is not None:
            self._downlink(instance=instance)
        else:
            self.task_instance_list.append(instance)

    def _downlink(self, instance):
        # todo: need to hand over downlink instance and port from which to pull data
        print("instance '%s' is connected over downlink '%s' port '%s'"
              % (instance.name, instance.downlink, instance.connection))
