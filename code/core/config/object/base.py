# base objects
#   are setting some basic functions and variables that should be inherited


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


class GaBaseModel(GaBase):
    def __init__(self, parent: int, type_id: int, member_list: list, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # vars for all models
        self.parent = parent
        self.type_id = type_id
        self.member_list = member_list
        self.setting_dict = setting_dict
        # vars from settings dict
        self.is_enabled = setting_dict['enabled']
        self.function = setting_dict['function']
        self.function_arg = setting_dict['function_arg']
        self.function_bin = setting_dict['function_bin']


class GaBaseDevice(GaBase):
    def __init__(self, model_instance, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # vars for all devices
        self.model_instance = model_instance
        self.is_locked = False
        self.setting_dict = setting_dict
        # vars from settings dict
        self.device_enabled = setting_dict['enabled']

    @property
    def is_enabled(self):
        if self.model_instance.is_enabled and self.device_enabled:
            return True
        return False

    @is_enabled.setter
    def is_enabled(self, value: bool):
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
    def __init__(self, model_instance, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # vars for all devices
        self.model_instance = model_instance
        self.is_locked = False
        self.setting_dict = setting_dict
        # vars from settings dict
        self.device_enabled = self.setting_dict['enabled']

    @property
    def is_enabled(self):
        if self.model_instance.is_enabled and self.device_enabled:
            return True
        return False

    @is_enabled.setter
    def is_enabled(self, value: bool):
        self.device_enabled = value


class GaBaseControllerModel(GaBase):
    def __init__(self, model_type: int, member_list: list, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # vars for all models
        self.model_type = model_type
        self.child_list = member_list
        self.setting_dict = setting_dict


class GaBaseControllerDevice(GaBase):
    def __init__(self, model_instance, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # vars for all devices
        self.model_instance = model_instance
        self.is_locked = False
        self.setting_dict = setting_dict
        # vars from settings dict
        self.device_enabled = self.setting_dict['enabled']

    @property
    def is_enabled(self):
        if self.model_instance.is_enabled and self.device_enabled:
            return True
        return False

    @is_enabled.setter
    def is_enabled(self, value: bool):
        self.device_enabled = value
