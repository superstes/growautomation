# connection device objects (used if devices cannot be addressed directly from the controller)
#   hold their model or device specific settings

from core.config.object.base import GaBaseDeviceModel, GaBaseDevice
from core.config.object.helper import set_attribute, set_parent_attribute


class GaConnectionModel(GaBaseDeviceModel):
    def __init__(self, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # model specific vars
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaConnectionModel
        )


class GaConnectionDevice(GaBaseDevice):
    parent_setting_list = ['script', 'script_arg', 'script_bin']
    setting_list = ['connection']

    def __init__(self, parent_instance: GaConnectionModel = None, **kwargs):
        # inheritance from superclasses
        super().__init__(parent_instance=parent_instance, **kwargs)
        # inheritance from model instance
        set_parent_attribute(
            child_instance=self,
            setting_list=self.parent_setting_list,
            obj=GaConnectionDevice
        )
        # device instance vars
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaConnectionDevice
        )
        self.active = False
