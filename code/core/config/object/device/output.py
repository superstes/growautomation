# output device objects (devices used for some kind of action)
#   hold their model or device specific settings

from core.config.object.base import *
from core.config.object.helper import *


class GaOutputDevice(GaBaseDevice):
    parent_setting_list = [
        'script', 'script_arg', 'script_bin', 'reverse', 'reverse_type', 'reverse_type_data', 'reverse_script', 'reverse_script_arg',
        'reverse_script_bin',
    ]
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
            obj=GaOutputDevice
        )
        # device instance vars
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaOutputDevice
        )
        self.active = False
        # self.reverse_timeout = parent_instance.reverse_timeout
        #   timeout if condition was not met -> to prevent problems caused by bad sensor data p.e.
        #   would need to start timed thread initially; link it to the instance; and stop it when the
        #   reverse action was processed via condition


class GaOutputModel(GaBaseDeviceModel):
    setting_list = [
        'script', 'script_arg', 'script_bin', 'reverse', 'reverse_type', 'reverse_type_data', 'reverse_script', 'reverse_script_arg',
        'reverse_script_bin',
    ]

    def __init__(self, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # model specific vars
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaOutputModel
        )
