# database object
#   holds information needed to connect to database
#   methods use submodules stored in $ga_root_path/core/config/db

from core.config.db.link import Go as Link
from core.config.db.check import Go as Check
from core.config.db.validate import Go as Validate


class GaDataDb:
    def __init__(self, file_config_dict: dict):
        try:
            self.connection_data_dict = {
                'ip': file_config_dict['sql_server_ip'],
                'port': file_config_dict['sql_server_port'],
                'user': file_config_dict['sql_user'],
                'secret': file_config_dict['sql_secret']
            }
        except IndexError as error_msg:
            # log error or whatever
            self._error(error_msg)

        self.link = None
        self._link()

    def _link(self):
        if Check(self.connection_data_dict).get():
            self.link = Link(self.connection_data_dict)
        else:
            self._error("Connection check failed.")

    @staticmethod
    def _validate(data: list) -> list:
        return Validate(data).get()

    def get(self, query: [str, list]) -> list:
        output = self.link.get(query)
        return self._validate(output)

    def put(self, command: [str, list]) -> bool:
        return self.link.put(command)

    def _error(self, msg):
        raise ConnectionError(msg)
