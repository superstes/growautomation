# will check for which input scripts to start
# filtering on enabled state, model grouping and area grouping

from core.device.log import device_logger
from core.device.area import area_filter


class Go:
    def __init__(self, instance, model_obj, device_obj, areas: list = None):
        self.instance = instance
        self.task_instance_list = []
        self.model_obj = model_obj
        self.device_obj = device_obj
        self.areas = areas
        self.logger = device_logger(addition=instance.name)

    def get(self) -> list:
        if isinstance(self.instance, self.model_obj):
            self._model()

        elif isinstance(self.instance, self.device_obj):
            self._device(instance=self.instance)

        else:
            self.logger.write(f"Instance \"{self.instance.name}\" matches neither provided objects", level=3)

        self.logger.write(f"Instance \"{self.instance.name}\" - unfiltered device list to process: \"{self.task_instance_list}\"", level=7)
        filtered_instance_list = area_filter(areas=self.areas, devices=self.task_instance_list)
        self.logger.write(f"Instance \"{self.instance.name}\" - filtered device list to process: \"{filtered_instance_list}\"", level=6)

        return filtered_instance_list

    def _model(self):
        for device_instance in self.instance.member_list:
            if device_instance.enabled == 1:
                self._device(instance=device_instance)

    def _device(self, instance):
        if instance.downlink is not None:
            self._downlink(instance=instance)

        else:
            self.task_instance_list.append({'device': instance})

    def _downlink(self, instance):
        downlink = instance.downlink

        if downlink.enabled == 0:
            self.logger.write(f"Downlink \"{downlink.name}\" of device \"{instance.name}\" is disabled", level=6)
            return None

        self.logger.write(f"Device \"{instance.name}\" is connected via downlink \"{downlink.name}\"", level=7)

        self.task_instance_list.append({'downlink': downlink, 'device': instance})
