# base objects
#   are setting some basic functions and variables that should be inherited

from core.config.object.helper import SETTING_DICT_EXCEPTION, SETTING_DICT_ERROR, set_attribute


class GaBase(object):
    reserved = ['name', 'description', 'state', 'object_id']

    def __init__(self, name, description, object_id):
        self.name = name
        self.description = description
        self.state = None
        self.object_id = object_id

    def __repr__(self):
        return f"{self.__class__.__name__}(id: '{self.object_id}', name: '{self.name}')"

    def __str__(self):
        return f"Object '{self.name}' as an instance of '{self.__class__.__name__}' - description: '{self.description}'"


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
        self.fail_count = 0
        self.fail_sleep = None
        self.setting_dict = setting_dict
        # vars from settings dict
        try:
            self.device_enabled = setting_dict['enabled']  # not dynamically set because of device-only attribute
        except SETTING_DICT_EXCEPTION as error_msg:
            raise SETTING_DICT_EXCEPTION(SETTING_DICT_ERROR % error_msg)

    @property
    def enabled(self):
        if self.parent_instance is None and self.device_enabled:
            return True
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
