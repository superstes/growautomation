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
#     E-Mail: contact@growautomation.at
#     Web: https://git.growautomation.at

# ga_version 0.4

from core.owl import DoSql
from core.smallant import Log
from core.smallant import debugger
from core.smallconfig import Config as FileConfig

from functools import lru_cache


class Config:
    def __init__(self, setting=None, nosql=False, output=None, belonging=None, filter=None, table=None, empty=False, exit=True,
                 local_debug=None):
        self.setting,  self.filter, self.belonging, self.output, self.table, self.exit = setting, filter, belonging, output, table, exit
        self.local_debug = local_debug
        self.empty, self.nosql = empty, nosql

    def _debug(self, output, level=1):
        if self.local_debug is None or self.local_debug is True:
            debugger(command=output, level=level)
        elif self.local_debug is False:
            return False

    def get(self, outtype=None):
        self._debug("config - get - input |setting '%s' '%s', nosql '%s' '%s', output '%s' '%s', belonging '%s' '%s', "
                    "filter '%s' '%s', table '%s' '%s'"
                    % (type(self.setting), self.setting, type(self.nosql), self.nosql, type(self.output), self.output,
                       type(self.belonging), self.belonging, type(self.filter), self.filter, type(self.table), self.table))
        parse_file_list = ['setuptype', 'sql_pwd', 'sql_local_user', 'sql_local_pwd', 'sql_agent_pwd', 'sql_admin_pwd']
        parse_failover_list = ['path_root', 'hostname', 'sql_server_port', 'sql_server_ip', 'sql_agent_user', 'sql_admin_user',
                               'sql_server_port', 'sql_sock']
        output = FileConfig(self.setting).get() if self.setting in parse_file_list else self._parse_failover() if self.setting in parse_failover_list else \
            self._parse_sql_custom() if self.nosql is False else self._error('all')
        if outtype is not None:
            try:
                if outtype == 'list' and type(output) != list:
                    output = [output]
                elif outtype == 'str' and type(output) != str:
                    output = str(output)
                elif outtype == 'int':
                    output = int(output)
                elif outtype == 'dict':
                    output = dict(output)
            except ValueError:
                output = str(output)
        self._debug("config - get - output |'%s' '%s'" % (type(output), output))
        return self._error('sql') if output is False else output

    def _error(self, parser_type):
        if self.empty: return False
        Log("%s parser could not find setting '%s'" % (parser_type.capitalize(), self.setting)).write()
        if self.exit:
            raise SystemExit("%s parser could not find setting %s" % (parser_type.capitalize(), self.setting))

    def _parse_sql(self, command=None):
        if command is not None:
            response = DoSql(command=command, local_debug=self.local_debug).start()
        else:
            response = DoSql("SELECT data FROM ga.Setting WHERE setting = '%s' and belonging = '%s';"
                             % (self.setting, FileConfig('hostname').get()), local_debug=self.local_debug).start()
        self._debug("config - parse_sql - output |'%s' '%s'" % (type(response), response))
        return self._error('sql') if response is False or response is None or response == '' else response

    def _parse_sql_custom(self):
        command, custom = ['SELECT', 'data', 'FROM ga.Setting WHERE'], False
        if self.table is not None:
            if self.table == 'grp': command = ['SELECT', 'description', 'FROM ga.Grp WHERE']
            elif self.table == 'member': command = ['SELECT', 'member', 'FROM ga.Member WHERE']
            elif self.table == 'object': command = ['SELECT', 'type', 'FROM ga.Object WHERE']
            elif self.table == 'data': command = ['SELECT', 'data', 'FROM ga.Data WHERE']
        if self.output is not None:
            command[1], custom = self.output, True
        if self.setting is not None:
            if self.table is not None:
                if self.table == 'member': command.append("gid = '%s'" % self.setting)
                elif self.table == 'grp': command.append("id = '%s'" % self.setting)
                elif self.table == 'object': command.append("name = '%s'" % self.setting)
                elif self.table == 'data': command.append("agent = '%s'" % self.setting)
            else: command.append("setting = '%s'" % self.setting)
            custom = True
        if self.belonging is not None:
            prefix = 'AND' if self.setting is not None else ''
            if self.table is not None:
                if self.table == 'member': insert = 'member'
                elif self.table == 'grp': insert = 'id'
                elif self.table == 'data': insert = 'agent'
            else: insert = 'belonging'
            command.append("%s %s = '%s'" % (prefix, insert, self.belonging))
            custom = True
        if self.filter is not None:
            prefix = 'AND ' if self.setting is not None or self.belonging is not None else ''
            command.append("%s%s" % (prefix, self.filter))
            custom = True
        if self.filter is None and self.setting is None:
            command.append('id IS NOT NULL')
        self._debug("config - sql_custom |custom '%s' '%s', command '%s' '%s'" % (type(custom), custom, type(command), command))
        return self._parse_sql(' '.join(command) + ';') if custom is True else self._parse_sql()

    @lru_cache()
    def _parse_hardcoded(self):
        config_dict = {'path_log': "%s/log" % FileConfig('path_root').get(), 'path_backup': "%s/backup" % FileConfig('path_root').get(), 'sql_server_port': '3306'}
        if FileConfig('setuptype').get() != 'agent':
            config_server_dict = {'sql_server_ip': '127.0.0.1'}
            config_dict = {**config_dict, **config_server_dict}
        if self.setting in config_dict.keys():
            for key, value in config_dict.items():
                if key.find(self.setting) != -1:
                    self._debug("config - hardcoded - found |'%s' '%s' '%s' '%s'" % (type(key), key, type(value), value))
                    return value
            return False
        else:
            self._debug('config - hardcoded - not found')
            return False

    def _parse_failover(self):
        parse_sql_output = self._parse_sql()
        if parse_sql_output is False or self.nosql is True:
            parse_file_output = FileConfig(self.setting).get()
            if parse_file_output is False or parse_file_output is None or parse_file_output == '':
                if self._parse_hardcoded() is False:
                    self._error('all')
                else:
                    output = self._parse_hardcoded()
                    self._debug("config - failover - output |'%s' '%s'" % (type(output), output))
                    return output
            else:
                self._debug("config - failover - output |'%s' '%s'" % (type(parse_file_output), parse_file_output))
                return parse_file_output
        else:
            self._debug("config - failover - output |'%s' '%s'" % (type(parse_sql_output), parse_sql_output))
            return parse_sql_output
