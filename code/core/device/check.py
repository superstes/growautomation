# will check for which input scripts to start
# basic filtering on enabled state and model grouping

from core.device.log import device_logger


class Go:
    def __init__(self, instance, model_obj, device_obj):
        self.instance = instance
        self.task_instance_list = []
        self.model_obj = model_obj
        self.device_obj = device_obj
        self.logger = device_logger(addition=instance.name)

    def get(self) -> list:
        if isinstance(self.instance, self.model_obj):
            self._model()
        elif isinstance(self.instance, self.device_obj):
            self._device(instance=self.instance)
        else:
            self.logger.write("Instance \"%s\" matches neither provided objects" % self.instance.name, level=6)

        self.logger.write("Instance \"%s\" - device list to process: \"%s\"" % (self.instance.name, self.task_instance_list), level=7)

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
            self.logger.write("Downlink \"%s\" of device \"%s\" is disabled" % (downlink.name, instance.name), level=6)
            return None

        self.logger.write("Device \"%s\" is connected via downlink \"%s\"" % (instance.name, downlink.name), level=7)

        self.task_instance_list.append({'downlink': downlink, 'device': instance})
