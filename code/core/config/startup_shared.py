# failover to config file when shared_vars were not yet initialized
# should only be used by low-level classes like logger that will be needed at the service startup

from core.config import shared as shared_vars
from core.config.object.data.file import GaDataFile
from core.config.object.core.controller import GaControllerDevice, GaControllerModel


# config set by service
def init():
    if not hasattr(shared_vars, 'SYSTEM'):
        shared_vars.init()
        config_file = GaDataFile().get()

        remove_key_list = ['name', 'description', 'object_id']

        for key in remove_key_list:
            if key in config_file:
                config_file.pop(key)

        for key, value in config_file.items():
            try:
                _ = int(value)
                config_file[key] = _

            except ValueError:
                continue

        shared_vars.SYSTEM = GaControllerDevice(
            setting_dict=config_file,
            object_id=0,
            name='TMP Controller',
            description='TMP Startup Controller Object',
            parent_instance=GaControllerModel()
        )
