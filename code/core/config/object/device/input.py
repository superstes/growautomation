# input device objects (devices used to get data)
#   hold their model or device specific settings

from core.config.object.base import *
from core.config.object.helper import *


class GaInputDevice(GaBaseDevice):
    def __init__(self, parent_instance, **kwargs):
        # inheritance from superclasses
        super().__init__(parent_instance=parent_instance, **kwargs)
        # inheritance from model instance
        parent_setting_list = ['function', 'function_arg', 'function_bin', 'start', 'unit']
        set_parent_attribute(
            child_instance=self,
            setting_list=parent_setting_list,
            obj=GaInputDevice
        )
        inheritence_setting_list = ['timer', 'unit', 'datatype']
        set_inherited_attribute(
            child_setting_dict=self.setting_dict,
            setting_list=inheritence_setting_list,
            child_instance=self,
            obj=GaInputDevice
        )
        # device instance vars
        setting_list = ['connection', 'downlink']
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=setting_list,
            instance=self,
            obj=GaInputDevice
        )


class GaInputModel(GaBaseModel):
    def __init__(self, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # model specific vars
        setting_list = ['timer', 'unit', 'datatype']
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=setting_list,
            instance=self,
            obj=GaInputModel
        )
