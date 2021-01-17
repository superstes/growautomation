# will check for which input scripts to start
# basic filtering on enabled state and model grouping

from core.utils.debug import debugger
from core.utils.debug import Log


class Go:
    def __init__(self, instance, model_obj, device_obj):
        self.instance = instance
        self.task_instance_list = []
        self.model_obj = model_obj
        self.device_obj = device_obj
        self.logger = Log()

    def get(self) -> list:
        if isinstance(self.instance, self.model_obj):
            self._model()
        elif isinstance(self.instance, self.device_obj):
            self._device(instance=self.instance)
        else:
            debugger("device-check | get | instance '%s' - matches neither provided objects '%s | %s'" % (self.instance.name, self.model_obj, self.device_obj))
            self.logger.write("instance '%s' matches neither provided objects" % self.instance.name)

        debugger("device-check | get | instance '%s' - instance_list to process: '%s'"
                 % (self.instance.name, self.task_instance_list))

        return self.task_instance_list

    def _model(self):
        for device_instance in self.instance.member_list:
            if device_instance.enabled:
                self._device(instance=device_instance)

    def _device(self, instance):
        if instance.downlink is not None:
            self._downlink(instance=instance)
        else:
            self.task_instance_list.append(instance)

    def _downlink(self, instance):
        # todo: need to hand over downlink instance and port from which to pull data
        self.logger.write("NOT YET IMPLEMENTED: 'connection devices'; instance '%s' is connected via downlink" % self.instance.name)
        debugger("device-check | _downlink | instance '%s' is connected over downlink '%s' port '%s'"
                 % (instance.name, instance.downlink, instance.connection))
