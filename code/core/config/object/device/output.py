# output device objects (devices used for some kind of action)
#   hold their model or device specific settings

from core.config.object.base import *
from core.config.object.helper import *


class GaOutputDevice(GaBaseDevice):
    REVERSE_TYPE_TIME = 1
    REVERSE_TYPE_CONDITION = 2

    def __init__(self, parent_instance, **kwargs):
        # inheritance from superclasses
        super().__init__(parent_instance=parent_instance, **kwargs)
        # inheritance from model instance
        parent_setting_list = ['function', 'function_arg', 'function_bin', 'start', 'reverse']
        set_parent_attribute(
            child_instance=self,
            setting_list=parent_setting_list,
            obj=GaOutputDevice
        )
        if self.reverse:  # not dynamically set because of dependencies
            self.reverse_type = parent_instance.reverse_type
            if self.reverse_type == self.REVERSE_TYPE_TIME:
                self.reverse_timer = parent_instance.reverse_timer
            elif self.reverse_type == self.REVERSE_TYPE_CONDITION:
                # self.reverse_timeout = parent_instance.reverse_timeout
                #   timeout if condition was not met -> to prevent problems caused by bad sensor data p.e.
                #   would need to start timed thread initially; link it to the instance; and stop it when the
                #   reverse action was processed via condition
                pass
            self.reverse_function = parent_instance.reverse_function
            self.reverse_function_arg = parent_instance.reverse_function_arg
            self.reverse_function_bin = parent_instance.reverse_function_bin
        # device instance vars
        setting_list = ['connection', 'downlink']
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=setting_list,
            instance=self,
            obj=GaOutputDevice
        )
        self.active = False


class GaOutputModel(GaBaseModel):
    def __init__(self, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # model specific vars
        try:  # not dynamically set because of dependencies
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
