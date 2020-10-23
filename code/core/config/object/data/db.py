# database object
#   holds information needed to connect to database
#   methods use submodules stored in $ga_root_path/core/config/db

from ....config.db.put import Go as Put
from ....config.db.get import Go as Get
from ....config.db.link import Go as Link
from ....config.db.check import Go as Check
from ....config.db.forge import Go as Forge
from ....config.db.validate import Go as Validate


class GaDataDb:
    def __init__(self, file_config_dict: dict):
        self.connection_data_dict = {
            'ip': file_config_dict['sql_server_ip'],
            'port': file_config_dict['sql_server_port'],
            'user': file_config_dict['sql_user'],
            'secret': file_config_dict['sql_secret']
        }

    def _link(self):
        Check(self.connection_data_dict).get()
        return Link(self.connection_data_dict).get()

    @staticmethod
    def _validate(data):
        return Validate(data).get()

    @staticmethod
    def _forge(data):
        return Forge.get(data)

    def get(self):
        Get(link=self._link).get()

    def put(self):
        Put(link=self._link).get()
