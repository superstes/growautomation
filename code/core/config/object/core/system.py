# controller objects
#   holds controller specific config

from core.config.object.base import GaBase
from core.config.object.helper import set_attribute


class GaAgent(GaBase):
    setting_list = [
        'sql_server', 'sql_port', 'sql_user', 'sql_secret', 'sql_database', 'log_level', 'debug', 'device_fail_count', 'device_fail_sleep', 'device_log',
        'path_root', 'path_home', 'path_log', 'svc_interval_status', 'svc_interval_reload', 'subprocess_timeout', 'version', 'version_detail',
    ]

    def __init__(self, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        self.setting_dict = setting_dict

        # vars from settings dict
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaAgent
        )


class GaServer(GaBase):
    setting_list = [
        'security', 'timezone', 'version', 'version_detail',
    ]

    def __init__(self, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        self.setting_dict = setting_dict

        # vars from settings dict
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaServer
        )
