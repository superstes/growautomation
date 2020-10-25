# connection device objects (used if devices cannot be addressed directly from the controller)
#   hold their model or device specific settings

from core.config.object.base import *


class GaConnectionModel(GaBaseModel):
    def __init__(self, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # model specific vars
        self.port_count = self.setting_dict['port_count']
        self.port_outtype = self.setting_dict['port_outtype']


class GaConnectionDevice(GaBaseDevice):
    def __init__(self, model_instance, **kwargs):
        # inheritance from superclasses
        super().__init__(model_instance=model_instance, **kwargs)
        # inheritance from model instance
        self.port_count = model_instance.port_count
        self.port_count = model_instance.port_outtype
        # device instance vars
        self.model_instance = model_instance
        self.connection = self.setting_dict['connection']
