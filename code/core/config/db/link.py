# connects to db
# gets connection settings passed from GaDataDb instance

from core.utils.process import subprocess

import mysql.connector
from time import sleep as time_sleep
from os import path as os_path
from functools import lru_cache


class Go:
    MARIADB_CONFIG_FILE = '/etc/mysql/mariadb.conf.d/50-server.cnf'

    def __init__(self, connection_data_dict):
        self.connection_data_dict = connection_data_dict
        self.cursor = None
        self.connection = None
        self._connect()

    def _connect(self) -> None:
        try:
            if self.connection_data_dict['ip'] == '127.0.0.1':
                if self.connection_data_dict['user'] == 'root':
                    try:
                        # local logon as root
                        # will only work if it is run with root privileges
                        _connection = mysql.connector.connect(
                            unix_socket=self._unixsock(),
                            user=self.connection_data_dict['user'],
                        )
                    except mysql.connector.Error:
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
                        passwd=self.connection_data_dict['secret']
                    )
            else:
                # remote logon
                _connection = mysql.connector.connect(
                    host=self.connection_data_dict['ip'],
                    port=self.connection_data_dict['port'],
                    user=self.connection_data_dict['user'],
                    passwd=self.connection_data_dict['secret']
                )

        except (mysql.connector.Error, mysql.connector.errors.InterfaceError, ValueError) as error_msg:
            self._error(error_msg)

        finally:
            self.connection = _connection
            self.cursor = _connection.cursor(buffered=True)

    def get(self, query: [str, list]) -> list:
        if type(query) == str:
            query_list = [query]
        else:
            query_list = query

        data_list = []

        try:
            for q in query_list:
                data = self._readcache(q)
                if len(query_list) > 1:
                    if type(data) is not None:
                        data_list.append(data)
                else:
                    data_list = data
        except (mysql.connector.Error, mysql.connector.errors.InterfaceError, ValueError) as error_msg:
            self._error(error_msg)

        return data_list  # list of tuples

    def put(self, command: [str, list]) -> bool:
        if type(command) == str:
            command_list = [str]
        else:
            command_list = command

        try:
            for c in command_list:
                self.cursor.execute(c)

            self.connection.commit()

        except (mysql.connector.Error, mysql.connector.errors.InterfaceError, ValueError) as error_msg:
            self._error(error_msg)

        return True

    def _error(self, msg: str):
        # log error or whatever
        try:
            self.connection.rollback()

        except UnboundLocalError:
            pass

        self.disconnect()

        raise ConnectionError(msg)

    def disconnect(self) -> None:
        self.cursor.close()
        self.connection.close()

    @lru_cache
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
