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

# ga_version0.3


from os import system as os_system
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from functools import lru_cache

from ga.core.smallant import LogWrite
from ga.core.config_parser_file import GetConfig


class DoSql:
    def __init__(self, command, write=False, debug=False):
        self.command = command
        self.write = write
        self.fallback = False
        self.debug = debug

    def __repr__(self):
        return str(self.prequesites())

    def connect(self, command=None):
        import mysql.connector
        if GetConfig("setuptype") == "agent":
            if self.fallback is True:
                connection = mysql.connector.connect(user="%s" % GetConfig("sql_local_user"), passwd="%s" % GetConfig("sql_local_pwd"))
            else:
                connection = mysql.connector.connect(host="%s" % GetConfig("sql_server_ip"), port="%s" % GetConfig("sql_server_port"),
                                                     user="%s" % GetConfig("sql_agent_user"), passwd="%s" % GetConfig("sql_agent_pwd"))
        else:
            connection = mysql.connector.connect(user="%s" % GetConfig("sql_admin_user"), passwd="%s" % GetConfig("sql_admin_pwd"))
        try:
            curser = connection.cursor(buffered=True)
            if command is None:
                command = self.command
            if self.write is False:
                @lru_cache()
                def readcache(doit):
                    curser.execute(doit)
                    return curser.fetchall()
                data = readcache(command)
            else:
                curser.execute(command)
                data = True
            curser.close()
            connection.close()
            return data
        except mysql.connector.Error as error:
            connection.rollback()
            LogWrite("Mysql connection failed.\nCommand: %s\nError: %s" % (command, error))
            if self.fallback is True:
                LogWrite("Server: %s, user %s" % ("127.0.0.1", GetConfig("mysql_localuser")))
            else:
                LogWrite("Server: %s, port %s, user %s" % (GetConfig("mysql.server_ip"), GetConfig("mysql.server_port"), GetConfig("mysql_user")))
            print(error)
            return False

    def prequesites(self):
        creds_ok = False
        if GetConfig("setuptype") != "agent":
            def running():
                output, error = subprocess_popen(["systemctl status mysql.service | grep 'Active:'"],
                                                 shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
                outputstr = output.decode("ascii")

                if outputstr.find("Active:") == -1:
                    return False
                elif outputstr.find("active (running)") != -1:
                    return True
                else:
                    return False
            whilecount = 0
            while True:
                if running() is False:
                    if whilecount == 0:
                        LogWrite("Trying to start mysql service.")
                        os_system("systemctl start mysql.service %s")
                    else:
                        LogWrite("Mysql service not running.")
                        raise SystemExit("Mysql service not active.")
                else:
                    break
                whilecount += 1
        whilecount = 0
        while creds_ok is False:
            if whilecount == 1 and GetConfig("setuptype") == "agent":
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
                if GetConfig("setuptype") == "agent":
                    table = "AgentConfig"
                else:
                    table = "ServerConfig"
                if self.write is False:
                    data = self.connect("SELECT * FROM ga.%s ORDER BY changed DESC LIMIT 10;" % table)
                else:
                    self.connect("INSERT INTO ga.AgentConfig (author, agent, setting, data) VALUES ('owl', '%s', 'conntest', 'ok');" % GetConfig("hostname"))
                    self.connect("DELETE FROM ga.AgentConfig WHERE author = 'owl' and agent = '%s';" % GetConfig("hostname"))
                    data = True
                if type(data) == list:
                    return True
                elif type(data) == bool:
                    return data
                else:
                    return False

            creds_ok = conntest()
            whilecount += 1
        return self.execute()

    def execute(self):
        if type(self.command) == str:
            return self.connect()
        elif type(self.command) == list:
            outputdict = {}
            anyfalse = True
            forcount = 1
            for command in self.command:
                output = self.connect()
                if self.debug is True:
                    outputdict[forcount][command] = output
                else:
                    outputdict[forcount] = output
                if output is False:
                    anyfalse = False
                forcount += 1
            if anyfalse is False:
                return False
            return outputdict
