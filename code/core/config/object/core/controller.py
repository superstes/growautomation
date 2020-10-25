# controller objects
#   holds controller specific config

from core.config.object.base import *


class GaControllerModel(GaBaseControllerModel):
    def __init__(self, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # model specific vars
        self.timezone = self.setting_dict['timezone']
        self.path_log = self.setting_dict['path_log']
        self.path_backup = self.setting_dict['path_backup']
        self.backup_log = self.setting_dict['backup_log']
        self.log_level = self.setting_dict['log_level']
        self.backup = self.setting_dict['backup']


class GaControllerDevice(GaBaseControllerDevice):
    def __init__(self, model_instance, **kwargs):
        # inheritance from superclasses
        super().__init__(model_instance=model_instance, **kwargs)
        # inheritance from model instance
        # device instance vars
        self.model_instance = model_instance
        #
        # 'name': 'gacon01', 'description': 'controller gacon01', 'enabled': True, 'setuptype': 'standalone',
        # 'path_root': '/etc/growautomation', 'path_log': '/var/log/growautomation', 'path_backup': '/mnt/backup',
        # 'install_timestamp': '2020-10-18', 'backup_log': False, 'python_path': '/usr/sbin/python3.8', 'log_level': 1,
        # 'version': '0.6', 'mnt_log_share': '/test', 'mnt_log_server': '192.168.1.1', 'mnt_log_pwd': '1234',
        # 'mnt_log_user': 'testuser', 'mnt_log_dom': 'nope', 'mnt_log_type': 'nfs', 'mnt_backup_share': '/testbak',
        # 'mnt_backup_server': '192.168.1.1', 'mnt_backup_pwd': '4321', 'mnt_backup_user': 'bakuser',
        # 'mnt_backup_dom': 'nope', 'mnt_backup_type': 'cifs', 'mnt_log': True, 'mnt_backup': False,
        # 'python_version': '3.8', 'sql_server_ip': '127.0.0.1', 'sql_server_port': 3306, 'sql_admin_user': 'gadmin',
        # 'sql_admin_pwd': 'nicey'
