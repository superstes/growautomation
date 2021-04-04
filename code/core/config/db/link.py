# connects to db
# gets connection settings passed from GaDataDb instance

from core.utils.process import subprocess
from core.utils.debug import Log

import mysql.connector
from time import sleep as time_sleep
from os import path as os_path
from functools import lru_cache


class Go:
    MARIADB_CONFIG_FILE = '/etc/mysql/mariadb.conf.d/50-server.cnf'
    SQL_EXCEPTION_TUPLE = (
        mysql.connector.errors.ProgrammingError,  # if sql syntax has an error
        mysql.connector.Error,
        mysql.connector.errors.InterfaceError,
        ValueError,
        FileNotFoundError  # if unix socket file does not exist
    )

    def __init__(self, connection_data_dict):
        self.connection_data_dict = connection_data_dict
        self.cursor = None
        self.connection = None
        self.logger = Log()
        self._connect()

    def _connect(self) -> bool:
        try:
            if self.connection_data_dict['server'] in ['127.0.0.1', 'localhost']:
                if self.connection_data_dict['user'] == 'root':
                    try:
                        # local logon as root
                        # will only work if it is run with root privileges
                        # should only be used in the setup and update
                        _connection = mysql.connector.connect(
                            unix_socket=self._unixsock(),
                            user=self.connection_data_dict['user'],
                        )
                        self.logger.write('Initiated sql connection via socket as root without password', level=8)

                    except self.SQL_EXCEPTION_TUPLE:
                        # if failed without password, try again with it
                        _connection = mysql.connector.connect(
                            unix_socket=self._unixsock(),
                            user=self.connection_data_dict['user'],
                            passwd=self.connection_data_dict['secret']
                        )
                        self.logger.write('Initiated sql connection via socket as root', level=8)

                else:
                    # local logon for default users
                    _connection = mysql.connector.connect(
                        unix_socket=self._unixsock(),
                        user=self.connection_data_dict['user'],
                        passwd=self.connection_data_dict['secret'],
                        database=self.connection_data_dict['database']
                    )
                    self.logger.write('Initiated sql connection to localhost', level=8)

            else:
                # remote logon
                _connection = mysql.connector.connect(
                    host=self.connection_data_dict['server'],
                    port=self.connection_data_dict['port'],
                    user=self.connection_data_dict['user'],
                    passwd=self.connection_data_dict['secret'],
                    database=self.connection_data_dict['database']
                )
                self.logger.write('Initiated sql connection to remote server', level=8)

        except self.SQL_EXCEPTION_TUPLE as error_msg:
            self._error(error_msg)

        try:
            self.connection = _connection
            self.cursor = _connection.cursor(buffered=True)
            return True

        except UnboundLocalError:
            self.logger.write('Connection instance could not be created.')
            raise ConnectionError('Connection instance not created')

    def get(self, query: [str, list]) -> list:
        if type(query) == str:
            query_list = [query]

        else:
            query_list = query

        self.logger.write(f"Query to execute: \"{query_list}\"", level=7)
        data_list = []

        try:
            for q in query_list:
                data = self._readcache(q)
                if len(query_list) > 1:
                    if type(data) is not None:
                        data_list.append(data)

                else:
                    data_list = data

        except self.SQL_EXCEPTION_TUPLE as error_msg:
            self._error(error_msg)

        self.logger.write(f"Query output: \"{data_list}\"", level=7)
        return data_list  # list of tuples

    def put(self, command: [str, list]) -> bool:
        if type(command) == str:
            command_list = [command]

        else:
            command_list = command

        self.logger.write(f"Query to execute: \"{command_list}\"", level=7)

        try:
            for cmd in command_list:
                self.cursor.execute(cmd)

            self.connection.commit()

        except self.SQL_EXCEPTION_TUPLE as error_msg:
            self._error(error_msg)

        return True

    def _error(self, msg: str):
        self.logger.write(f"SQL connection error: \"{msg}\"", level=3)

        try:
            self.connection.rollback()

        except (UnboundLocalError, AttributeError):
            pass

        raise ConnectionError(msg)

    @lru_cache(maxsize=16)
    def _readcache(self, query: str):
        self.cursor.execute(query)

        if self.cursor.rowcount < 1:
            return None

        else:
            return self.cursor.fetchall()

    @classmethod
    def _unixsock(cls):
        try:
            with open(cls.MARIADB_CONFIG_FILE, 'r') as _:
                for line in _.readlines():
                    if line.find('socket') != -1:
                        sock = line.split('=')[1].strip()
                        break

                if not sock:
                    return False

            if os_path.exists(sock) is False:
                if subprocess(command="systemctl status mysql.service | grep 'Active:'").find('Active: inactive') != -1:
                    if subprocess('systemctl start mysql.service').find('Not able to start') != -1:
                        return False

                    time_sleep(5)

            return sock

        except IndexError:
            return False

    def __del__(self):
        try:
            self.cursor.close()

        except (UnboundLocalError, AttributeError, ReferenceError):
            pass

        try:
            self.connection.close()
            self.logger.write('SQL connection closed', level=8)

        except (UnboundLocalError, AttributeError, ReferenceError):
            pass
