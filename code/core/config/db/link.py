# connects to db
# gets connection settings passed from GaDataDb instance

from core.utils.process import subprocess
from core.utils.debug import debugger
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
        self._connect()

    def _connect(self) -> bool:
        try:
            debugger("config-db-link | _connect | user '%s', database '%s', ip '%s', port '%s'"
                     % (self.connection_data_dict['user'], self.connection_data_dict['database'],
                        self.connection_data_dict['server'], self.connection_data_dict['port']))

            if self.connection_data_dict['server'] == '127.0.0.1':
                if self.connection_data_dict['user'] == 'root':
                    try:
                        # local logon as root
                        # will only work if it is run with root privileges
                        # should only be used in the setup and update
                        _connection = mysql.connector.connect(
                            unix_socket=self._unixsock(),
                            user=self.connection_data_dict['user'],
                        )
                    except self.SQL_EXCEPTION_TUPLE:
                        # if failed without password, try again with it
                        _connection = mysql.connector.connect(
                            unix_socket=self._unixsock(),
                            user=self.connection_data_dict['user'],
                            passwd=self.connection_data_dict['secret']
                        )
                else:
                    # local logon for default users
                    _connection = mysql.connector.connect(
                        unix_socket=self._unixsock(),
                        user=self.connection_data_dict['user'],
                        passwd=self.connection_data_dict['secret'],
                        database=self.connection_data_dict['database']
                    )
            else:
                # remote logon
                _connection = mysql.connector.connect(
                    host=self.connection_data_dict['server'],
                    port=self.connection_data_dict['port'],
                    user=self.connection_data_dict['user'],
                    passwd=self.connection_data_dict['secret'],
                    database=self.connection_data_dict['database']
                )

        except self.SQL_EXCEPTION_TUPLE as error_msg:
            self._error(error_msg)

        finally:
            try:
                self.connection = _connection
                self.cursor = _connection.cursor(buffered=True)
                return True
            except UnboundLocalError:
                raise ConnectionError('Connection instance not created')

    def get(self, query: [str, list]) -> list:
        if type(query) == str:
            query_list = [query]
        else:
            query_list = query

        debugger("config-db-link | get | query to process '%s'" % query_list)

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

        debugger("config-db-link | get | output '%s'" % data_list)

        return data_list  # list of tuples

    def put(self, command: [str, list]) -> bool:
        if type(command) == str:
            command_list = [command]
        else:
            command_list = command

        debugger("config-db-link | put | command to process '%s'" % command_list)

        try:
            for c in command_list:
                self.cursor.execute(c)

            self.connection.commit()

        except self.SQL_EXCEPTION_TUPLE as error_msg:
            self._error(error_msg)

        return True

    def _error(self, msg: str):
        debugger("config-db-link | _error | received error '%s'" % msg)
        # log error or whatever

        try:
            self.connection.rollback()

        except (UnboundLocalError, AttributeError):
            pass

        self.disconnect()

        raise ConnectionError(msg)

    def disconnect(self) -> None:
        # todo: implement destructor and remove all manual disconnect call + make it private

        try:
            self.cursor.close()
            self.connection.close()

            debugger('config-db-link | disconnect | disconnected from db')

        except (UnboundLocalError, AttributeError):
            pass

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
