# output device objects (devices used for some kind of action)
#   hold their model or device specific settings

from core.config.object.base import *


class GaActorModel(GaBaseModel):
    def __init__(self, reverse: bool, reverse_type: int, reverse_data, reverse_function, reverse_function_arg,
                 reverse_function_bin, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # model specific vars
        self.reverse = reverse
        self.reverse_type = reverse_type
        self.reverse_data = reverse_data
        self.reverse_function = reverse_function
        self.reverse_function_arg = reverse_function_arg
        self.reverse_function_bin = reverse_function_bin


class GaActorDevice(GaBaseDevice):
    def __init__(self, model_instance, connection, downlink, **kwargs):
        # inheritance from superclasses
        super().__init__(model_instance=model_instance, **kwargs)
        # inheritance from model instance
        self.function = model_instance.function
        self.function_arg = model_instance.function_arg
        self.function_bin = model_instance.function_bin
        self.reverse = model_instance.reverse
        self.reverse_type = model_instance.reverse_type
        self.reverse_data = model_instance.reverse_data
        self.reverse_function = model_instance.reverse_function
        self.reverse_function_arg = model_instance.reverse_function_arg
        self.reverse_function_bin = model_instance.reverse_function_bin
        # device instance vars
        self.connection = connection
        self.downlink = downlink
