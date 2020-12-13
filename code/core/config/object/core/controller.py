# controller objects
#   holds controller specific config

from core.config.object.base import *
from core.config.object.helper import *


class GaControllerDevice(GaBase):
    def __init__(self, parent_instance, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # specific vars
        self.parent_instance = parent_instance
        self.setting_dict = setting_dict
        # vars from settings dict
        overwrite_inherited_attribute(
            child_setting_dict=self.setting_dict,
            setting_list=self.parent_instance.setting_list,
            child_instance=self,
            obj=GaControllerDevice
        )

        # name, description
        # enabled, setuptype, path_root, path_log, path_backup, install_timestamp, backup_log, python_path,
        # python_version, log_level, version, mnt_log_share, mnt_log_server, mnt_log_pwd, mnt_log_user, mnt_log_domain,
        # mnt_log_type, -,,- with backup mount, mnt_log, sql_server_ip, sql_server_port, sql_user, sql_pwd, backup time/interval


class GaControllerModel(GaBase):
    setting_list = [
        'name', 'description', 'path_root', 'path_log', 'path_backup', 'sql_server', 'sql_port', 'sql_user', 'sql_secret', 'sql_database',
        'log_level', 'debug', 'security', 'backup', 'timezone'
    ]

    def __init__(self, member_list: list, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # specific vars
        self.member_list = member_list
        self.setting_dict = setting_dict
        # vars from settings dict
        set_attribute(
            setting_dict=self.setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaControllerModel
        )
