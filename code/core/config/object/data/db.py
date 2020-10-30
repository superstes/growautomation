# database object
#   holds information needed to connect to database
#   methods use submodules stored in $ga_root_path/core/config/db

from core.config.db.link import Go as Link
from core.config.db.check import Go as Check
from core.config.db.validate import Go as Validate
from core.config.object.data.file import GaDataFile
from core.utils.debug import debugger


class GaDataDb:
    def __init__(self):
        file_config_dict = GaDataFile().get()
        try:
            # debug input
            self.connection_data_dict = {
                'server': file_config_dict['sql_server'],
                'port': file_config_dict['sql_port'],
                'user': file_config_dict['sql_user'],
                'secret': file_config_dict['sql_secret'],
                'database': file_config_dict['sql_database']
            }
        except IndexError as error_msg:
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
        debugger("config-object-data-db | _error | received error '%s'" % msg)
        # log error or whatever
        raise ConnectionError(msg)

    def disconnect(self):
        self.link.disconnect()
