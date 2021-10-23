# failover to config file when shared_vars were not yet initialized
# should only be used by low-level classes like logger that will be needed at the service startup

from core.config import shared as config
from core.config.object.data.file import GaDataFile
from core.config.object.core.system import GaAgent, GaServer


# config set by service
def init():
    if not hasattr(config, 'SYSTEM'):
        config.init()
        config_file = GaDataFile().get()

        construction_dict = {}

        for setting in GaAgent.setting_list:
            if setting in config_file:
                try:
                    _ = int(config_file[setting])
                    construction_dict[setting] = _

                except ValueError:
                    construction_dict[setting] = config_file[setting]

        config.AGENT = GaAgent(
            setting_dict=construction_dict,
            object_id=0,
            name='TMP Agent',
            description='TMP Startup Agent Object',
        )

        config.SERVER = GaServer(
            setting_dict={
                'security': 1,
                'timezone': 'Europe/Vienna',
                'version': 1.0,
                'version_detail': 'a3e9e6383bdb23f4f9560a7ef805f299c80dd2fa',
            },
            object_id=0,
            name='TMP Server',
            description='TMP Startup Server Object',
        )
