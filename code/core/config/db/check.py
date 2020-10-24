# should check for db connectivity problems before connecting

from core.config.db.link import Go as Link

import mysql.connector
from random import choice as random_choice
import socket


class Go:
    TEST_READ_COMMAND = 'SELECT * FROM ga.test LIMIT 10;'
    TEST_WRITE_RAND_TBL = ''.join(random_choice('0123456789') for _ in range(5))
    TEST_WRITE_COMMAND_LIST = [
        'CREATE TABLE ga.test_%s;' % TEST_WRITE_RAND_TBL,
        'DROP TABLE ga.test_%s;' % TEST_WRITE_RAND_TBL
    ]

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
            return self._error(msg="Error while executing command '%s':\n'%s'"
                                   % (self.TEST_READ_COMMAND, error_msg))

        if type(output) is list and len(output) > 0:
            return True

        return False

    def _test_write(self) -> bool:
        # may need to add a ignore argument for server/agent installation (since server db will be r/o for agent)
        try:
            for c in self.TEST_WRITE_COMMAND_LIST:
                if not self.link.put(c):
                    return self._error(msg="Error while executing command '%s'" % c)

            return True

        except ConnectionError as error_msg:
            return self._error(msg="Error while testing write:\n'%s'" % error_msg)

    def _test_network(self) -> bool:
        # check <L5 connectivity
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = connection.connect_ex(
                    (self.connection_data_dict['ip'],
                     self.connection_data_dict['port'])
            )

            connection.close()
        except socket.error as error_msg:
            return self._error(msg="Error while testing network connection:\n'%s'" % error_msg)

        if result == 0:
            return True

        return False

    @staticmethod
    def _error(msg):
        # log error or whatever
        return False
