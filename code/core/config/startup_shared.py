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

        construction_dict = {}

        for setting in GaControllerDevice.setting_list:
            if setting in config_file:
                try:
                    _ = int(config_file[setting])
                    construction_dict[setting] = _

                except ValueError:
                    construction_dict[setting] = config_file[setting]

        shared_vars.SYSTEM = GaControllerDevice(
            setting_dict=construction_dict,
            object_id=0,
            name='TMP Controller',
            description='TMP Startup Controller Object',
            parent_instance=GaControllerModel()
        )
