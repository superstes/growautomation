# will check for which input scripts to start
# basic filtering on enabled state and model grouping

from core.config import shared as shared_vars
from core.utils.debug import MultiLog, Log, debugger


class Go:
    def __init__(self, instance, model_obj, device_obj):
        self.instance = instance
        self.task_instance_list = []
        self.model_obj = model_obj
        self.device_obj = device_obj

        if shared_vars.SYSTEM.device_log == 1:
            self.logger = MultiLog([Log(), Log(typ='device', addition=self.instance.name)])
        else:
            self.logger = Log()

    def get(self) -> list:
        if isinstance(self.instance, self.model_obj):
            self._model()
        elif isinstance(self.instance, self.device_obj):
            self._device(instance=self.instance)
        else:
            debugger("device-check | get | instance \"%s\" - matches neither provided objects '%s | %s'" % (self.instance.name, self.model_obj, self.device_obj))
            self.logger.write("instance \"%s\" matches neither provided objects" % self.instance.name)

        debugger("device-check | get | instance \"%s\" - instance_list to process: \"%s\""
                 % (self.instance.name, self.task_instance_list))

        return self.task_instance_list

    def _model(self):
        for device_instance in self.instance.member_list:
            if device_instance.enabled == 1:
                self._device(instance=device_instance)

    def _device(self, instance):
        if instance.downlink is not None:
            self._downlink(instance=instance)
        else:
            self.task_instance_list.append(instance)

    def _downlink(self, instance):
        downlink = instance.downlink

        if downlink.enabled == 0:
            debugger("device-check | _downlink | downlink \"%s\" of device \"%s\" is disabled" % (downlink.name, instance.name))
            self.logger.write("downlink \"%s\" of device \"%s\" is disabled" % (downlink.name, instance.name))
            return None

        self.logger.write("'connection devices'; instance \"%s\" is connected via downlink \"%s\"" % (instance.name, downlink.name), level=6)
        debugger("device-check | _downlink | instance \"%s\" is connected over downlink \"%s\" port \"%s\""
                 % (instance.name, instance.downlink, instance.connection))

        self.task_instance_list.append({'downlink': downlink, 'device': instance})
