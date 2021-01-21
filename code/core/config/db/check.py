# should check for db connectivity problems before connecting

from core.config.db.link import Go as Link
from core.config.db.template import DB_CHECK_DICT
from core.utils.debug import debugger

import mysql.connector
from random import choice as random_choice
import socket


class Go:
    TEST_READ_COMMAND = DB_CHECK_DICT['read']
    TEST_WRITE_COMMAND_LIST = DB_CHECK_DICT['write']

    def __init__(self, connection_data_dict):
        self.connection_data_dict = connection_data_dict
        self.link = Link(connection_data_dict)

    def get(self) -> bool:
        try:
            if not self._test_network() or not self._test_read() or not self._test_write():
                return False

        except (mysql.connector.Error, ConnectionError) as error_msg:
            return self._error(msg=error_msg)

        finally:
            return True

    def _test_read(self) -> bool:
        try:
            output = self.link.get(self.TEST_READ_COMMAND)

        except ConnectionError as error_msg:
            return self._error(msg="Error while executing command \"%s\":\n\"%s\""
                                   % (self.TEST_READ_COMMAND, error_msg))

        if type(output) is list and len(output) > 0:
            return True

        return False

    def _test_write(self) -> bool:
        # may need to add a ignore argument for server/agent installation (since server db will be r/o for agent)
        try:
            random_table = ''.join(random_choice('0123456789') for _ in range(5))
            for c in self.TEST_WRITE_COMMAND_LIST:
                if not self.link.put(c % random_table):
                    return self._error(msg="Error while executing command \"%s\"" % c)

            return True

        except ConnectionError as error_msg:
            return self._error(msg="Error while testing write:\n\"%s\"" % error_msg)

    def _test_network(self) -> bool:
        # check <L5 connectivity
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = connection.connect_ex(
                    (self.connection_data_dict['server'],
                     self.connection_data_dict['port'])
            )

            connection.close()
        except socket.error as error_msg:
            return self._error(msg="Error while testing network connection:\n\"%s\"" % error_msg)

        if result == 0:
            return True

        return False

    @staticmethod
    def _error(msg):
        debugger("config-db-check | _error | received error \"%s\"" % msg)
        # log error or whatever
        return False
