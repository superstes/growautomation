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

try:
    from core.smallant import Log
    from core.smallconfig import Config
    from core.smallant import debugger
    from core.smallant import process
except (ImportError, ModuleNotFoundError):
    from smallant import Log
    from smallconfig import Config
    from smallant import debugger
    from smallant import process

from random import choice as random_choice
from os import path as os_path
from time import sleep as time_sleep
from functools import lru_cache


class DoSql:
    def __init__(self, command, write=False, user=None, pwd=None, exit=True, hostname=None, setuptype=None):
        self.command, self.write, self.user, self.pwd, self.exit = command, write, user, pwd, exit
        if hostname is None:
            self.hostname = Config('hostname').get()
        else: self.hostname = hostname
        if setuptype is None:
            self.setuptype = Config('setuptype').get()
        else: self.setuptype = setuptype
        self.fallback = False

    def start(self):
        def systemd_check(typ):
            mysql_status = process('systemctl status mysql.service')
            if typ == 'ok':
                if mysql_status.find("active (running)") != -1: return True
                else: return False
            elif typ == 'dead':
                if mysql_status.find('failed') != -1 or mysql_status.find('could not be found') != -1:
                    return True
                else: return False
        whilecount, conntest_result = 0, False
        while True:
            if systemd_check('ok') is False:
                if whilecount > 0:
                    if systemd_check('dead') is True: return False
                debugger('owl - start |mysql not running')
                process('systemctl start mysql.service')
            else: break
            if whilecount > 2: break
            time_sleep(.5)
            whilecount += 1
        whilecount = 0
        while conntest_result is False:
            if whilecount == 1 and self.setuptype == 'agent':
                debugger('owl - start |failing over to local db')
                Log('Failing over to local read-only database').write()
                self.fallback = True
            if self.fallback is True and self.write is True:
                Log('Error connecting to database. Write operations are not allowed to local fallback database. '
                    'Check you sql server connection.').write()
                if self.exit:
                    raise SystemExit('Error connecting to database. Write operations are not allowed to local fallback database. '
                                     'Check you sql server connection.')
                else: return False

            if whilecount > 2:
                Log("Error connecting to database. Check content of %ga_root/core/core.conf file for correct sql login credentials.").write()
                if self.exit:
                    raise SystemExit("Error connecting to database. Check content of %ga_root/core/core.conf file for correct sql login credentials.")
                else: return False

            if self.write is False:
                if self.user == 'root':
                    data = self._connect('SELECT * FROM mysql.help_category LIMIT 10;', connect_debug=False)
                else:
                    data = self._connect('SELECT * FROM ga.Setting LIMIT 10;', connect_debug=False)
            else:
                if self.user == 'root':
                    rand_db_nr = ''.join(random_choice('0123456789') for _ in range(20))
                    self._connect("CREATE DATABASE test_%s;" % rand_db_nr, connect_debug=False)
                    data = self._connect("DROP DATABASE test_%s;" % rand_db_nr, connect_debug=False)
                else:
                    self._connect("INSERT IGNORE INTO ga.Setting (author, belonging, setting, data) VALUES ('owl', '%s', 'conntest', 'ok');"
                                  % self.hostname, connect_debug=False)
                    data = self._connect("DELETE FROM ga.Setting WHERE author = 'owl' and setting = 'conntest';", connect_debug=False)
            debugger("owl - start |conntest output '%s' '%s'" % (type(data), data), level=2)
            if type(data) == list or type(data) == str: conntest_result = True
            elif type(data) == bool: conntest_result = data
            else: conntest_result = False
            debugger("owl - start |conntest result '%s' " % conntest_result)
            whilecount += 1
        return self._execute()

    def _execute(self):
        debugger("owl - execute |command '%s' '%s'" % (type(self.command), self.command))
        if type(self.command) == str:
            return self._connect()
        elif type(self.command) == list:
            outputdict, anyfalse, forcount = {}, True, 1
            for command in self.command:
                output = self._connect(command)
                outputdict[forcount] = output
                if output is False: anyfalse = False
                forcount += 1
            return False if not anyfalse else outputdict

    def _check_config(self, setting):
        output = Config(setting).get()
        if output is False:
            debugger("owl - config_check |unable to get value for setting '%s'" % setting)
            Log("Unable to obtain value for setting '%s' - exiting sql connection").write()
            raise ValueError
        else:
            return output

    def _connect(self, command=None, connect_debug=True):
        import mysql.connector
        try:
            if self.user is not None:
                if self.user == 'root':
                    connection = mysql.connector.connect(unix_socket=self._unixsock(), user=self.user)
                else:
                    if self.setuptype == 'agent':
                        connection = mysql.connector.connect(host="%s" % self._check_config('sql_server_ip'),
                                                             port="%s" % self._check_config('sql_server_port'),
                                                             user=self.user, passwd=self.pwd)
                    else:
                        connection = mysql.connector.connect(unix_socket=self._unixsock(), user=self.user, passwd=self.pwd)
            elif self.setuptype == 'agent':
                if self.fallback is True: connection = mysql.connector.connect(user="%s" % self._check_config('sql_local_user'),
                                                                               passwd="%s" % self._check_config('sql_local_pwd'))
                else: connection = mysql.connector.connect(unix_socket=self._unixsock(), host="%s" % self._check_config('sql_server_ip'),
                                                           port="%s" % self._check_config('sql_server_port'),
                                                           user="%s" % self._check_config('sql_agent_user'),
                                                           passwd="%s" % self._check_config('sql_agent_pwd'))
            else: connection = mysql.connector.connect(unix_socket=self._unixsock(), user="%s" % self._check_config('sql_admin_user'),
                                                       passwd="%s" % self._check_config('sql_admin_pwd'))
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
        except (mysql.connector.Error, mysql.connector.errors.InterfaceError, ValueError) as error:
            debugger("owl - connect |error '%s'" % error)
            try:
                connection.rollback()
            except UnboundLocalError: pass
            Log("Mysql connection failed.\nUser: %s\nCommand: %s\nError: %s" % (self.user, command, error)).write()
            return False

    def _unixsock(self):
        try:
            sql_sock = process(command="cat /etc/mysql/mariadb.conf.d/50-server.cnf | grep 'socket                  ='").split('=')[1].strip()
            if os_path.exists(sql_sock) is False:
                if process(command="systemctl status mysql.service | grep 'Active:'").find('Active: inactive') != -1:
                    if process('systemctl start mysql.service').find('Not able to start') != -1:
                        return False
                    time_sleep(5)
            return sql_sock
        except IndexError: return False

    def find(self, searchfor):
        debugger("owl - find |input '%s' '%s' '%s'" % (type(searchfor), searchfor, self.command))
        if type(self.command) == str:
            data = str(self._execute())
            output = data.find(searchfor)
        elif type(self.command) == list:
            output, sqllist = -1, self._execute()
            for x in sqllist:
                if x.find(searchfor) != -1: output +=1
        debugger("owl - find |output '%s' '%s'" % (type(output), output))
        return output


def sql_replace(data_dict, table='setting', debug=False):
    # first entry in data_dict = value that should be changed
    debugger("owl - replace |input dict '%s'" % data_dict, hard_debug=debug)
    if table == 'setting': table = 'ga.Setting'
    elif table == 'grp': table = 'ga.Grp'
    elif table == 'member': table = 'ga.Member'
    elif table == 'object': table = 'ga.Object'
    elif table == 'data': table = 'ga.Data'
    elif table == 'tmp': table = 'ga.Temp'
    else: return False
    command, entrycount = [], 0
    for key, value in data_dict.items():
        append_str = []
        if entrycount > 1: append_str.append('AND')
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