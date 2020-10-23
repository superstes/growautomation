# base objects
#   are setting some basic functions and variables that should be inherited


class GaBase(object):
    def __init__(self, name, description, object_id, enabled):
        self.name = name
        self.description = description
        self.state = None
        self.object_id = object_id
        if enabled is not None:  # if a subclass wants needs more logic
            self.is_enabled = enabled

    def __repr__(self):
        return "%s(id: '%s', name: '%s')" % (self.__class__.__name__, self.object_id, self.name)

    def __str__(self):
        return "Object '%s' as an Instance of '%s'; Description: '%s'" \
               % (self.name, self.__class__.__name__, self.description)


class GaBaseModel(GaBase):
    def __init__(self, function: str, function_arg, function_bin: str, model_type: int, child_list: list, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # vars for all models
        self.function = function
        self.function_arg = function_arg
        self.function_bin = function_bin
        self.model_type = model_type
        self.child_list = child_list


class GaBaseDevice(GaBase):
    def __init__(self, model_instance, enabled, **kwargs):
        # inheritance from superclasses
        super().__init__(enabled=None, **kwargs)
        # vars for all devices
        self.model_instance = model_instance
        self.is_locked = False
        self.device_enabled = enabled

    @property
    def is_enabled(self):
        if self.model_instance.is_enabled and self.device_enabled:
            return True
        return False

    @is_enabled.setter
    def is_enabled(self, value: bool):
        self.device_enabled = value


class GaBaseCoreModel(GaBase):
    def __init__(self, model_type: int, child_list: list, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # vars for all models
        self.model_type = model_type
        self.child_list = child_list


class GaBaseCoreDevice(GaBase):
    def __init__(self, model_instance, enabled, **kwargs):
        # inheritance from superclasses
        super().__init__(enabled=None, **kwargs)
        # vars for all devices
        self.model_instance = model_instance
        self.is_locked = False
        self.device_enabled = enabled

    @property
    def is_enabled(self):
        if self.model_instance.is_enabled and self.device_enabled:
            return True
        return False

    @is_enabled.setter
    def is_enabled(self, value: bool):
        self.device_enabled = value


class GaBaseControllerModel(GaBase):
    def __init__(self, model_type: int, child_list: list, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # vars for all models
        self.model_type = model_type
        self.child_list = child_list


class GaBaseControllerDevice(GaBase):
    def __init__(self, model_instance, enabled, **kwargs):
        # inheritance from superclasses
        super().__init__(enabled=None, **kwargs)
        # vars for all devices
        self.model_instance = model_instance
        self.is_locked = False
        self.device_enabled = enabled

    @property
    def is_enabled(self):
        if self.model_instance.is_enabled and self.device_enabled:
            return True
        return False

    @is_enabled.setter
    def is_enabled(self, value: bool):
        self.device_enabled = value
