# base objects
#   are setting some basic functions and variables that should be inherited

from core.config.object.helper import *


class GaBase(object):
    def __init__(self, name, description, object_id):
        self.name = name
        self.description = description
        self.state = None
        self.object_id = object_id

    def __repr__(self):
        return "%s(id: '%s', name: '%s')" % (self.__class__.__name__, self.object_id, self.name)

    def __str__(self):
        return "Object '%s' as an Instance of '%s'; Description: '%s'" \
               % (self.name, self.__class__.__name__, self.description)


class GaBaseDeviceModel(GaBase):
    def __init__(self, member_list: list, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # vars for all models
        self.member_list = member_list
        self.setting_dict = setting_dict
        # vars from settings dict
        self.setting_list = ['enabled', 'script', 'script_arg', 'script_bin']
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaBaseDeviceModel
        )


class GaBaseDevice(GaBase):
    def __init__(self, parent_instance, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # vars for all devices
        self.parent_instance = parent_instance
        self.locked = False
        self.setting_dict = setting_dict
        # vars from settings dict
        try:
            self.device_enabled = setting_dict['enabled']  # not dynamically set because of device-only attribute
        except SETTING_DICT_EXCEPTION as error_msg:
            raise SETTING_DICT_EXCEPTION(SETTING_DICT_ERROR % error_msg)

    @property
    def enabled(self):
        if self.parent_instance.enabled and self.device_enabled:
            return True
        return False

    @enabled.setter
    def enabled(self, value: bool):
        self.device_enabled = value


class GaBaseCoreModel(GaBase):
    def __init__(self, model_type: int, member_list: list, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # vars for all models
        self.model_type = model_type
        self.member_list = member_list
        self.setting_dict = setting_dict


class GaBaseCoreDevice(GaBase):
    def __init__(self, parent_instance, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # vars for all devices
        self.parent_instance = parent_instance
        self.locked = False
        self.setting_dict = setting_dict
        # vars from settings dict
        setting_list = ['enabled']
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=setting_list,
            instance=self,
            obj=GaBaseCoreDevice
        )
