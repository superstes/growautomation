# core objects
#   holds settings needed by the core modules

from core.config.object.base import *


class GaCoreModel(GaBaseCoreModel):
    def __init__(self, setting_dict, **kwargs):
        # inheritance from superclasses
        super().__init__(enabled=None, **kwargs)
        # model specific vars
        self.setting_dict = setting_dict


class GaCoreDevice(GaBaseCoreDevice):
    def __init__(self, model_instance, **kwargs):
        # inheritance from superclasses
        super().__init__(model_instance=model_instance, **kwargs)
        # inheritance from model instance
        # device instance vars
        self.model_instance = model_instance
