# controller objects
#   holds controller specific config

from core.config.object.base import *


class GaControllerModel(GaBase):
    def __init__(self, member_list: list, setting_dict: dict, parent: int, type_id: int, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # specific vars
        self.type_id = type_id
        self.parent = parent
        self.member_list = member_list
        self.setting_dict = setting_dict
        # vars from settings dict
        print("controller model: %s" % self.setting_dict)
        self.setting_list = [
            'path_root', 'path_log', 'path_backup', 'sql_server', 'sql_port', 'sql_user', 'sql_secret', 'sql_database',
            'log_level', 'security', 'debug', 'backup', 'timezone'
        ]
        try:
            for key in self.setting_list:
                if key not in self.setting_dict:
                    raise SETTING_DICT_EXCEPTION("Setting '%s' was not provided" % key)
                else:
                    setattr(self, key, self.setting_dict[key])

        except SETTING_DICT_EXCEPTION as error_msg:
            raise SETTING_DICT_EXCEPTION(SETTING_DICT_ERROR % (self.name, self.object_id, GaControllerModel, error_msg))


class GaControllerDevice(GaBase):
    def __init__(self, model_instance, setting_dict: dict, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # specific vars
        self.model_instance = model_instance
        self.setting_dict = setting_dict
        # vars from settings dict
        try:
            for key in self.model_instance.setting_list:
                if key in self.setting_dict:
                    setattr(self, key, self.setting_dict[key])
                else:
                    setattr(self, key, self.model_instance.setting_dict[key])

        except SETTING_DICT_EXCEPTION as error_msg:
            raise SETTING_DICT_EXCEPTION(SETTING_DICT_ERROR % (self.name, self.object_id, GaControllerDevice, error_msg))

        # name, description
        # enabled, setuptype, path_root, path_log, path_backup, install_timestamp, backup_log, python_path,
        # python_version, log_level, version, mnt_log_share, mnt_log_server, mnt_log_pwd, mnt_log_user, mnt_log_domain,
        # mnt_log_type, -,,- with backup mount, mnt_log, sql_server_ip, sql_server_port, sql_user, sql_pwd
