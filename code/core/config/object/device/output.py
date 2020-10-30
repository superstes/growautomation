# output device objects (devices used for some kind of action)
#   hold their model or device specific settings

from core.config.object.base import *
from core.output.output import Go as Output


class GaOutputModel(GaBaseModel):
    def __init__(self, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # model specific vars
        try:
            self.reverse = self.setting_dict['reverse']
            if self.reverse:
                self.reverse_type = self.setting_dict['reverse_type']
                if self.reverse_type == 1:
                    self.reverse_timer = self.setting_dict['reverse_timer']
                self.reverse_function = self.setting_dict['reverse_function']
                self.reverse_function_arg = self.setting_dict['reverse_function_arg']
                self.reverse_function_bin = self.setting_dict['reverse_function_bin']
        except SETTING_DICT_EXCEPTION as error_msg:
            raise SETTING_DICT_EXCEPTION(SETTING_DICT_ERROR % (self.name, self.object_id, GaOutputModel, error_msg))


class GaOutputDevice(GaBaseDevice):
    def __init__(self, model_instance, **kwargs):
        # inheritance from superclasses
        super().__init__(model_instance=model_instance, **kwargs)
        # inheritance from model instance
        self.function = model_instance.function
        self.function_arg = model_instance.function_arg
        self.function_bin = model_instance.function_bin
        self.reverse = model_instance.reverse
        if self.reverse:
            self.reverse_type = model_instance.reverse_type
            if self.reverse_type == 1:
                self.reverse_timer = model_instance.reverse_timer
            self.reverse_function = model_instance.reverse_function
            self.reverse_function_arg = model_instance.reverse_function_arg
            self.reverse_function_bin = model_instance.reverse_function_bin
        # device instance vars
        try:
            self.connection = self.setting_dict['connection']
            self.downlink = self.setting_dict['downlink']
        except SETTING_DICT_EXCEPTION as error_msg:
            raise SETTING_DICT_EXCEPTION(SETTING_DICT_ERROR % (self.name, self.object_id, GaOutputDevice, error_msg))

    def start(self, instance):
        Output(instance=instance).start()
