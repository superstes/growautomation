# input device objects (devices used to get data)
#   hold their model or device specific settings

from ..base import *


class GaSensorDevice(GaBaseDevice):
    def __init__(self, model_instance, timer: int, connection, downlink, **kwargs):
        # inheritance from superclasses
        super().__init__(model_instance=model_instance, **kwargs)
        # inheritance from model instance
        self.function = model_instance.function
        self.function_arg = model_instance.function_arg
        self.function_bin = model_instance.function_bin
        self.unit = model_instance.unit
        # device instance vars
        if timer is not None:
            self.timer = timer
        else: self.timer = model_instance.timer
        self.connection = connection
        self.downlink = downlink


class GaSensorModel(GaBaseModel):
    def __init__(self, timer: int, unit: str, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # model specific vars
        self.timer = timer
        self.unit = unit
