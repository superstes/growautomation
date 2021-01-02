# input device objects (devices used to get data)
#   hold their model or device specific settings

from core.config.object.base import *
from core.config.object.helper import *


class GaInputDevice(GaBaseDevice):
    parent_setting_list = ['script', 'script_arg', 'script_bin', 'unit', 'datatype']
    inheritance_setting_list = ['timer']
    setting_list = ['connection']

    def __init__(self, parent_instance, downlink, **kwargs):
        # inheritance from superclasses
        super().__init__(parent_instance=parent_instance, **kwargs)
        # specific vars
        self.downlink = downlink
        # inheritance from model instance
        set_parent_attribute(
            child_instance=self,
            setting_list=self.parent_setting_list,
            obj=GaInputDevice
        )
        overwrite_inherited_attribute(
            child_setting_dict=self.setting_dict,
            setting_list=self.inheritance_setting_list,
            child_instance=self,
            obj=GaInputDevice
        )
        # device instance vars
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaInputDevice
        )


class GaInputModel(GaBaseDeviceModel):
    def __init__(self, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        self.setting_list.extend(['unit', 'datatype', 'timer'])
        # model specific vars
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaInputModel
        )
