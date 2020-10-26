# input device objects (devices used to get data)
#   hold their model or device specific settings

from core.config.object.base import *
from core.input.input import Go as Input


class GaInputDevice(GaBaseDevice):
    def __init__(self, model_instance, **kwargs):
        # inheritance from superclasses
        super().__init__(model_instance=model_instance, **kwargs)
        # inheritance from model instance
        self.function = model_instance.function
        self.function_arg = model_instance.function_arg
        self.function_bin = model_instance.function_bin
        self.unit = model_instance.unit
        if 'timer' in self.setting_dict:
            self.timer = self.setting_dict['timer']
        else:
            self.timer = model_instance.timer
        # device instance vars
        self.connection = self.setting_dict['connection']
        self.downlink = self.setting_dict['downlink']


class GaInputModel(GaBaseModel):
    def __init__(self, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # model specific vars
        self.timer = self.setting_dict['timer']
        self.unit = self.setting_dict['unit']

    def start(self, instance):
        Input(instance=instance).start()
