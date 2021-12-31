# database object
#   holds information needed to connect to database
#   methods use submodules stored in $ga_root_path/core/config/db

from core.config.db.link import Go as Link
from core.config.db.check import Go as Check
from core.config import shared as config
from core.utils.debug import log, censor


class GaDataDb:
    def __init__(self):
        try:
            self.connection_data_dict = {
                'server': config.AGENT.sql_server,
                'port': config.AGENT.sql_port,
                'user': config.AGENT.sql_user,
                'secret': config.AGENT.sql_secret,
                'database': config.AGENT.sql_database
            }

            log(
                f"DB connection config: "
                f"server => \"{self.connection_data_dict['server']}\" "
                f"port => \"{self.connection_data_dict['port']}\" "
                f"user => \"{self.connection_data_dict['user']}\" "
                f"database => \"{self.connection_data_dict['database']}\"",
                level=7
            )

        except IndexError as error_msg:
            self._error(msg=error_msg)

        self.link = None
        self._link()

    def _link(self):
        if Check(self.connection_data_dict).get():
            self.link = Link(self.connection_data_dict)

        else:
            self._error("Connection check failed.")

    def get(self, query: [str, list]) -> list:
        return self.link.get(query)

    def put(self, command: [str, list]) -> bool:
        return self.link.put(command)

    @staticmethod
    def _error(msg):
        log(f"Received error \"{msg}\"")
        raise ConnectionError(censor(msg))
