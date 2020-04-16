#!/usr/bin/python3
# This file is part of Growautomation
#     Copyright (C) 2020  René Pascal Rath
#
#     Growautomation is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#     E-Mail: rene.rath@growautomation.at
#     Web: https://git.growautomation.at

# ga_version 0.3

from os import system as os_system
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from functools import lru_cache
from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe
from time import sleep as time_sleep

from ga.core.smallant import LogWrite
from ga.core.config_parser_file import GetConfig


LogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), level=2)


class DoSql:
    def __init__(self, command, write=False, debug=False):
        self.command = command
        self.write = write
        self.fallback = False
        self.debug = debug

    def start(self):
        creds_ok = False
        if GetConfig("setuptype") != "agent":
            def running():
                output, error = subprocess_popen(["systemctl status mysql.service | grep 'Active:'"],
                                                 shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
                outputstr = output.decode("ascii")
                return False if outputstr.find("Active:") == -1 else True if outputstr.find("active (running)") != -1 else False
            whilecount = 0
            while True:
                if running() is False:
                    debugger("owl - prequesits |mysql not running")
                    if whilecount == 0:
                        LogWrite("Trying to start mysql service.")
                        os_system("systemctl start mysql.service %s")
                    else:
                        LogWrite("Not able to start mysql service.")
                        raise SystemExit("Not able to start mysql service.")
                else: break
                time_sleep(5)
                whilecount += 1
        whilecount = 0
        while creds_ok is False:
            if whilecount == 1 and GetConfig("setuptype") == "agent":
                debugger("owl - prequesits |failing over to local db")
                LogWrite("Failing over to local read-only database")
                self.fallback = True
            if self.fallback is True and self.write is True:
                LogWrite("Error connecting to database. Write operations are not allowed to local fallback database. Check you sql server connection.")
                raise SystemExit("Error connecting to database. Write operations are not allowed to local fallback database. "
                                 "Check you sql server connection.")
            if whilecount > 2:
                LogWrite("Error connecting to database. Check content of %ga_root/core/core.conf file for correct sql login credentials.")
                raise SystemExit("Error connecting to database. Check content of %ga_root/core/core.conf file for correct sql login credentials.")

            def conntest():
                if self.write is False: data = self.connect("SELECT * FROM ga.Setting ORDER BY changed DESC LIMIT 10;", connect_debug=False)
                else:
                    self.connect("INSERT INTO ga.Setting (author, belonging, setting, data) VALUES ('owl', '%s', 'conntest', 'ok');" % GetConfig("hostname"), connect_debug=False)
                    self.connect("DELETE FROM ga.Setting WHERE author = 'owl' and belonging = '%s';" % GetConfig("hostname"), connect_debug=False)
                    data = True
                result = True if type(data) == list else data if type(data) == bool else False
                debugger("owl - prequesits |conntest %s %s" % (type(result), result))
                return result

            creds_ok = conntest()
            whilecount += 1
        return self.execute()

    def execute(self):
        debugger("owl - execute |command %s %s" % (type(self.command), self.command))
        if type(self.command) == str:
            return self.connect()
        elif type(self.command) == list:
            outputdict, anyfalse, forcount = {}, True, 1
            for command in self.command:
                output = self.connect(command)
                outputdict[forcount] = output
                if output is False: anyfalse = False
                forcount += 1
            return False if not anyfalse else outputdict

    def connect(self, command=None, connect_debug=True):
        import mysql.connector
        if GetConfig("setuptype") == "agent":
            if self.fallback is True: connection = mysql.connector.connect(user="%s" % GetConfig("sql_local_user"), passwd="%s" % GetConfig("sql_local_pwd"))
            else: connection = mysql.connector.connect(host="%s" % GetConfig("sql_server_ip"), port="%s" % GetConfig("sql_server_port"),
                                                       user="%s" % GetConfig("sql_agent_user"), passwd="%s" % GetConfig("sql_agent_pwd"))
        else: connection = mysql.connector.connect(user="%s" % GetConfig("sql_admin_user"), passwd="%s" % GetConfig("sql_admin_pwd"))
        try:
            cursor = connection.cursor(buffered=True)
            if command is None: command = self.command
            if connect_debug: debugger("owl - connect |command %s %s" % (type(command), command))
            if self.write is False:
                @lru_cache()
                def readcache(doit):
                    cursor.execute(doit)
                    if cursor.rowcount < 0: return False
                    else:
                        fetch, data_list = cursor.fetchall(), []
                        for row_tuple in fetch:
                            if len(row_tuple) == 1:
                                if row_tuple[0]: data_list.append(row_tuple[0])
                            else: data_list.append(row_tuple)
                        return str(data_list[0]) if len(data_list) == 1 else data_list
                data = readcache(command)
            else:
                cursor.execute(command)
                connection.commit()
                data = True
            cursor.close()
            connection.close()
            if connect_debug: debugger("owl - connect |output %s %s" % (type(data), data))
            return data
        except mysql.connector.Error as error:
            if connect_debug: debugger("owl - connect |error %s" % error)
            connection.rollback()
            LogWrite("Mysql connection failed.\nCommand: %s\nError: %s" % (command, error))
            if self.fallback is True: LogWrite("Server: %s, user %s" % ("127.0.0.1", GetConfig("mysql_localuser")))
            else: LogWrite("Server: %s, port %s, user %s" % (GetConfig("mysql.server_ip"), GetConfig("mysql.server_port"), GetConfig("mysql_user")))
            return False

    def find(self, searchfor):
        debugger("owl - find |input %s %s" % (type(searchfor), searchfor))
        if type(self.command) == str:
            data = str(self.execute())
            output = data.find(searchfor)
        elif type(self.command) == list:
            sqllist = self.execute()
            output = []
            for x in sqllist: output.append(x.find(searchfor))
        debugger("owl - find |output %s %s" % (type(output), output))
        return output


@lru_cache()
def debug_check():
    command = "SELECT data FROM ga.Setting WHERE setting = 'debug' AND belonging = 'service';"
    sql = DoSql(command)
    debug_state = sql.connect(command=command, connect_debug=False)
    return True if debug_state == "1" else False


def debugger(command):
    if debug_check() is True:
        if type(command) == str:
            print(command)
        elif type(command) == list:
            [print(call) for call in command]
