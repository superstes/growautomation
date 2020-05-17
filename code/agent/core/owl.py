#!/usr/bin/python3.8
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

# ga_version 0.4
# sql module

from smallant import LogWrite
from smallconfig import Config
from smallant import debugger
from smallant import process

from os import path as os_path
from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe
from time import sleep as time_sleep
from functools import lru_cache

LogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), level=2)


class DoSql:
    def __init__(self, command, write=False, user=None, pwd=None, exit=True, hostname=None, setuptype=None):
        self.command, self.write, self.user, self.pwd, self.exit = command, write, user, pwd, exit
        if hostname is None:
            self.hostname = Config("hostname").get()
        else: self.hostname = hostname
        if setuptype is None:
            self.setuptype = Config("setuptype").get()
        else: self.setuptype = setuptype
        self.fallback = False

    def start(self):
        def systemd_check(typ):
            mysql_status = process("systemctl status mysql.service")
            if typ == "ok":
                if mysql_status.find("active (running)") != -1: return True
                else: return False
            elif typ == "dead":
                if mysql_status.find("failed") != -1 or mysql_status.find("could not be found") != -1:
                    return True
                else: return False
        whilecount, conntest_result = 0, False
        while True:
            if systemd_check("ok") is False:
                if whilecount > 0:
                    if systemd_check("dead") is True: return False
                debugger("owl - start |mysql not running")
                process("systemctl start mysql.service")
            else: break
            if whilecount > 2: break
            time_sleep(.5)
            whilecount += 1
        whilecount = 0
        while conntest_result is False:
            if whilecount == 1 and self.setuptype == "agent":
                debugger("owl - start |failing over to local db")
                LogWrite("Failing over to local read-only database")
                self.fallback = True
            if self.fallback is True and self.write is True:
                LogWrite("Error connecting to database. Write operations are not allowed to local fallback database. Check you sql server connection.")
                if self.exit:
                    raise SystemExit("Error connecting to database. Write operations are not allowed to local fallback database. "
                                     "Check you sql server connection.")
                else: return False

            if whilecount > 2:
                LogWrite("Error connecting to database. Check content of %ga_root/core/core.conf file for correct sql login credentials.")
                if self.exit:
                    raise SystemExit("Error connecting to database. Check content of %ga_root/core/core.conf file for correct sql login credentials.")
                else: return False

            if self.write is False: data = self.connect("SELECT * FROM mysql.help_category LIMIT 10;", connect_debug=False)
            else:
                self.connect("INSERT INTO ga.Setting (author, belonging, setting, data) VALUES ('owl', '%s', 'conntest', 'ok');" % self.hostname, connect_debug=False)
                self.connect("DELETE FROM ga.Setting WHERE author = 'owl' and belonging = '%s';" % self.hostname, connect_debug=False)
                data = True
            conntest_result = True if type(data) == list else data if type(data) == bool else False
            debugger("owl - start |conntest '%s' '%s'" % (type(conntest_result), conntest_result))
            whilecount += 1
        return self.execute()

    def execute(self):
        debugger("owl - execute |command '%s' '%s'" % (type(self.command), self.command))
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
        try:
            if self.user is not None:
                if self.user == "root":
                    connection = mysql.connector.connect(unix_socket=self.unixsock(), user=self.user)
                else:
                    if self.setuptype == "agent":
                        connection = mysql.connector.connect(host="%s" % Config("sql_server_ip").get(), port="%s" % Config("sql_server_port").get(),
                                                             user=self.user, passwd=self.pwd)
                    else:
                        connection = mysql.connector.connect(unix_socket=self.unixsock(), user=self.user, passwd=self.pwd)
            elif self.setuptype == "agent":
                if self.fallback is True: connection = mysql.connector.connect(user="%s" % Config("sql_local_user").get(), passwd="%s" % Config("sql_local_pwd").get())
                else: connection = mysql.connector.connect(unix_socket=self.unixsock(), host="%s" % Config("sql_server_ip").get(), port="%s" % Config("sql_server_port").get(),
                                                           user="%s" % Config("sql_agent_user").get(), passwd="%s" % Config("sql_agent_pwd").get())
            else: connection = mysql.connector.connect(unix_socket=self.unixsock(), user="%s" % Config("sql_admin_user").get(), passwd="%s" % Config("sql_admin_pwd").get())
            cursor = connection.cursor(buffered=True)
            if command is None: command = self.command
            if connect_debug: debugger("owl - connect |command '%s' '%s'" % (type(command), command))
            if self.write is False:
                @lru_cache()
                def readcache(doit):
                    cursor.execute(doit)
                    if cursor.rowcount < 1: return False
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
            if connect_debug: debugger("owl - connect |output '%s' '%s'" % (type(data), data))
            return data
        except (mysql.connector.Error, mysql.connector.errors.InterfaceError) as error:
            if connect_debug: debugger("owl - connect |error '%s'" % error)
            try:
                connection.rollback()
            except UnboundLocalError: pass
            LogWrite("Mysql connection failed.\nUser: %s\nCommand: %s\nError: %s" % (self.user, command, error))
            return False

    def unixsock(self):
        try:
            sql_sock = process(command="cat /etc/mysql/mariadb.conf.d/50-server.cnf | grep 'socket                  ='").split("=")[1].strip()
            if os_path.exists(sql_sock) is False:
                if process(command="systemctl status mysql.service | grep 'Active:'").find("Active: inactive") != -1:
                    if process("systemctl start mysql.service").find("Not able to start") != -1:
                        return False
                    time_sleep(5)
            return sql_sock
        except IndexError: return False

    def find(self, searchfor):
        debugger("owl - find |input '%s' '%s'" % (type(searchfor), searchfor))
        if type(self.command) == str:
            data = str(self.execute())
            output = data.find(searchfor)
        elif type(self.command) == list:
            output, sqllist = -1, self.execute()
            for x in sqllist:
                if x.find(searchfor) != -1: output +=1
        debugger("owl - find |output '%s' '%s'" % (type(output), output))
        return output


def sql_replace(data_dict, table="setting", debug=False):
    # first entry in data_dict = value that should be changed
    debugger("owl - replace |input dict '%s'" % data_dict, hard_debug=debug)
    if table == "setting": table = "ga.Setting"
    elif table == "group": table = "ga.Grouping"
    elif table == "object": table = "ga.Object"
    elif table == "data": table = "ga.Data"
    elif table == "tmp": table = "ga.Temp"
    else: return False
    command, entrycount = [], 0
    for key, value in data_dict.items():
        append_str = []
        if entrycount > 1: append_str.append("AND")
        if entrycount > 0:
            append_str.append("%s = '%s'" % (key, value))
            command.append(' '.join(append_str))
        entrycount += 1
    debugger("owl - replace |command '.. %s';" % ' '.join(command), hard_debug=debug)
    if DoSql("SELECT data FROM %s WHERE %s;" % (table, ' '.join(command))).start() is False:
        insert_command = "INSERT INTO %s (%s) VALUES ('%s');" % (table, ','.join(list(data_dict.keys())), '\',\''.join(data_dict.values()))
        DoSql(insert_command, write=True).start()
        debugger("owl - replace |insert command '%s'" % insert_command, hard_debug=debug)
        return True
    else:
        update_command = "UPDATE %s SET %s = '%s' WHERE %s;" % (table, list(data_dict.keys())[0], list(data_dict.values())[0], ' '.join(command))
        DoSql(update_command, write=True).start()
        debugger("owl - replace |update command '%s'" % update_command, hard_debug=debug)
        return True