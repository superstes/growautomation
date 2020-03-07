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
#ga_version0.3
import mysql.connector
from os import system as os_system
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from ga import ant
from ga import config
from functools import lru_cache


class do:
    def __init__(self, command, write=False, debug=False):
        self.command = command
        self.write = write
        self.fallback = False
        self.debug = debug
        self.ga_mysql_prequesites()

    def ga_mysql_connection(self, command=None):
        connection = mysql.connector.connect(host=config.mysql.server_ip, port=config.mysql.server_port, user=config.mysql.user, passwd=config.mysql.pwd)
        try:
            curser = connection.cursor(buffered=True)
            if command is None:
                command = self.command
            if self.write is False:
                @lru_cache()
                def ga_mysql_connection_readcache(doit):
                    curser.execute(doit)
                    return curser.fetchall()
                data = ga_mysql_connection_readcache(command)
            else:
                curser.execute(command)
                data = True
            curser.close()
            connection.close()
            return data
        except mysql.connector.Error as error:
            connection.rollback()
            ant.log("Mysql connection failed.\nCommand: %s\nError: %s" % (command, error))
            print(error)
            return False

    def ga_mysql_prequesites(self):
        creds_ok = False
        whilecount = 0
        while creds_ok is False:
            if self.fallback is True and self.write is True:
                ant.log("Error connecting to database. Write operations are not allowed to local fallback database. Check you sql server connection.")
                raise SystemExit("Error connecting to database. Write operations are not allowed to local fallback database. "
                                 "Check you sql server connection.")
            if whilecount > 2:
                ant.log("Error connecting to database. Check content of %ga_root/main/main.conf file for correct sql login credentials.")
                raise SystemExit("Error connecting to database. Check content of %ga_root/main/main.conf file for correct sql login credentials.")

            def ga_mysql_conntest(*args, **kwargs):
                if config.setuptype == "agent":
                    table = "AgentConfig"
                else:
                    table = "ServerConfig"
                if self.write is False:
                    data = self.ga_mysql_connection("SELECT * FROM ga.%s ORDER BY changed DESC LIMIT 10;" % table)
                else:
                    self.ga_mysql_connection("INSERT INTO ga.AgentConfig (author, agent, setting, data) VALUES ('owl', '%s', 'conntest', 'ok');"
                                             % config.hostname)
                    self.ga_mysql_connection("DELETE FROM ga.AgentConfig WHERE author = 'owl' and agent = '%s';" % config.hostname)
                    data = True
                logvars = config.mysql.server_ip, config.mysql.server_port, config.mysql.user
                if type(data) == list:
                    return True
                elif type(data) == bool:
                    if data is False:
                        ant.log("Sql connection to server %s:%s failed with user %s" % logvars)
                    return data
                else:
                    ant.log("Sql connection to server %s:%s failed with user %s" % logvars)
                    return False

            creds_ok = ga_mysql_conntest()
            whilecount += 1

        if config.setuptype != "agent":
            def ga_mysql_running():
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
                if ga_mysql_running() is False:
                    if whilecount == 0:
                        ant.log("Trying to start mysql service.")
                        os_system("systemctl start mysql.service %s" % ant.log_redirect)
                    else:
                        ant.log("Mysql service not running.")
                        raise SystemExit("Mysql service not active.")
                whilecount += 1

        self.ga_mysql_execute()

    def ga_mysql_execute(self):
        if type(self.command) == str:
            return self.ga_mysql_connection()
        elif type(self.command) == list:
            outputdict = {}
            anyfalse = True
            forcount = 1
            for command in self.command:
                output = self.ga_mysql_connection()
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
