# connection device objects (used if devices cannot be addressed directly from the controller)
#   hold their model or device specific settings

from core.config.object.base import *


class GaDownlinkModel(GaBaseModel):
    def __init__(self, port_count: int, port_outtype: int, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # model specific vars
        self.port_count = port_count
        self.port_outtype = port_outtype


class GaDownlinkDevice(GaBaseDevice):
    def __init__(self, model_instance, connection, **kwargs):
        # inheritance from superclasses
        super().__init__(model_instance=model_instance, **kwargs)
        # inheritance from model instance
        self.port_count = model_instance.port_count
        self.port_count = model_instance.port_outtype
        # device instance vars
        self.model_instance = model_instance
        self.connection = connection
