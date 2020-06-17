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

# ga_version 0.5

from core.handlers.database import Interact as DoSql
from core.shared.smallant import format_output
from core.handlers.debug import Log
from core.handlers.debug import debugger
from core.handlers.smallconfig import Config as FileConfig

from functools import lru_cache


class Config:
    def __init__(self, setting=None, nosql=False, output=None, belonging=None, filter=None, table=None,
                 empty=False, exit=True, local_debug=None, distributed=False):
        self.setting,  self.filter, self.belonging, self.output = setting, filter, belonging, output
        self.table, self.exit, self.local_debug, self.distributed = table, exit, local_debug, distributed
        self.empty, self.nosql, self.sql_custom = empty, nosql, False

    def _debug(self, output, level=1):
        if self.local_debug is None or self.local_debug is True:
            debugger(command=output, level=level)
        elif self.local_debug is False:
            return False

    def get(self, outtype=None):
        self._debug("config - get - input |setting: '%s', nosql: '%s', output: '%s', belonging: '%s', filter: '%s', table: '%s', "
                    "empty: '%s', exit: '%s', local_debug: '%s', distributed: '%s'"
                    % (self.setting, self.nosql, self.output, self.belonging, self.filter, self.table, self.empty, self.exit,
                       self.local_debug, self.distributed))
        parse_file_list = ['setuptype', 'sql_pwd', 'sql_local_user', 'sql_local_pwd', 'sql_agent_pwd', 'sql_admin_pwd']
        parse_failover_list = ['path_root', 'hostname', 'sql_server_port', 'sql_server_ip', 'sql_agent_user', 'sql_admin_user',
                               'sql_server_port', 'sql_sock']

        if self.setting in parse_file_list:
            output = FileConfig(self.setting).get()
        elif self.setting in parse_failover_list:
            output = self._parse_failover()
        elif self.nosql is False:
            if self.distributed:
                output = self._parse_sql_distributed_setting()
            else: output = self._parse_sql_custom()
        else: output = self._error('all')

        if outtype is not None:
            output = format_output(typ=outtype, data=output)

        self._debug("config - get - output |'%s' '%s'" % (type(output), output))
        if output is False: return self._error('sql')
        else: return output

    def _error(self, parser_type):
        Log("%s parser could not find setting '%s'" % (parser_type.capitalize(), self.setting)).write()
        if self.empty or self.exit: return False

    def _parse_sql(self, command=None):
        if command is not None:
            response = DoSql(command=command, local_debug=self.local_debug).start()
        else:
            response = DoSql("SELECT data FROM ga.Setting WHERE setting = '%s' and belonging = '%s';"
                             % (self.setting, FileConfig('hostname').get()), local_debug=self.local_debug).start()
        self._debug("config - parse_sql - output |'%s' '%s'" % (type(response), response))
        if response is False or response is None or response == '':
            return self._error('sql')
        else: return response

    def _parse_sql_custom(self):
        command = self._parse_sql_table()
        if self.output is not None:
            command[1] = self.output
            self.sql_custom = True
        if self.setting is not None:
            command.append(self._parse_sql_setting())
        if self.belonging is not None:
            command.append(self._parse_sql_belonging())
        if self.filter is not None:
            command.append(self._parse_sql_filter())
        if self.filter is None and self.setting is None:
            command.append('id IS NOT NULL')

        self._debug("config - sql_custom |command '%s' '%s'" % (type(command), command))
        if self.sql_custom:
            return self._parse_sql(' '.join(command) + ';')
        else: return self._parse_sql()

    def _parse_sql_distributed_setting(self):
        setting_table_dict = {'ga.Setting': None, 'ga.GrpSetting': 'grpsetting'}
        if self.table is not None and self.table not in setting_table_dict.values():
            return False
        output_list = []
        for table, shorty in setting_table_dict.items():
            self.table = shorty
            output = self._parse_sql_custom()
            if type(output) == list:
                if len(output) == 0: continue
                else: output_list.extend(output)
            elif type(output) == str:
                output_list.append(output)
        return output_list

    def _parse_sql_table(self):
        if self.table is not None:
            if self.table == 'grp':
                output = ['SELECT', 'name', 'FROM ga.Grp WHERE']
            elif self.table == 'grpsetting':
                output = ['SELECT', 'data', 'FROM ga.GrpSetting WHERE']
            elif self.table == 'member':
                output = ['SELECT', 'member', 'FROM ga.Member WHERE']
            elif self.table == 'object':
                output = ['SELECT', 'type', 'FROM ga.Object WHERE']
            elif self.table == 'data':
                output = ['SELECT', 'data', 'FROM ga.Data WHERE']
            else: output = ['SELECT', 'data', 'FROM ga.Setting WHERE']
            self.sql_custom = True
        else: output = ['SELECT', 'data', 'FROM ga.Setting WHERE']
        return output

    def _parse_sql_setting(self):
        if self.table is not None and self.table.find('Setting') == -1:
            if self.table == 'member':
                output = "gid = '%s'" % self.setting
            elif self.table == 'grp':
                output = "id = '%s'" % self.setting
            elif self.table == 'object':
                output = "name = '%s'" % self.setting
            elif self.table == 'data':
                output = "agent = '%s'" % self.setting
            else: output = "setting = '%s'" % self.setting
            self.sql_custom = True
        else: output = "setting = '%s'" % self.setting
        return output

    def _parse_sql_belonging(self):
        prefix = 'AND' if self.setting is not None else ''
        if self.table is not None:
            if self.table == 'member': insert = 'member'
            elif self.table == 'grp': insert = 'id'
            elif self.table == 'data': insert = 'agent'
            else: insert = 'belonging'
        else: insert = 'belonging'
        self.sql_custom = True
        return "%s %s = '%s'" % (prefix, insert, self.belonging)

    def _parse_sql_filter(self):
        if self.setting is not None or self.belonging is not None: prefix = 'AND '
        else: prefix = ''
        self.sql_custom = True
        return "%s%s" % (prefix, self.filter)

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
