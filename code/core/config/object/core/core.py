# core objects
#   holds settings needed by the core modules

from core.config.object.base import GaBaseCoreDevice, GaBaseCoreModel


class GaCoreModel(GaBaseCoreModel):
    def __init__(self, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)


class GaCoreDevice(GaBaseCoreDevice):
    def __init__(self, parent_instance, **kwargs):
        # inheritance from superclasses
        super().__init__(parent_instance=parent_instance, **kwargs)
        # inheritance from model instance
        # device instance vars
        self.parent_instance = parent_instance
