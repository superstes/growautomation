#!/usr/bin/python
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

from functools import lru_cache
from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe

from ga.core.owl import DoSql
from ga.core.smallant import LogWrite
from ga.core.config_parser_file import GetConfig as parse_file

LogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), loglevel=2)


class GetConfig(object):
    def __init__(self, setting=None, nosql=False, output=None, belonging=None, filter=None, table=None):
        self.setting = setting
        self.nosql = nosql
        self.filter = filter
        self.belonging = belonging
        self.output = output
        self.table = table

    def __repr__(self):
        parse_file_list = ["setuptype", "sql_pwd", "sql_local_user", "sql_local_pwd", "sql_agent_pwd", "sql_admin_pwd"]
        parse_failover_list = ["path_root", "hostname", "sql_server_port", "sql_server_ip", "sql_agent_user", "sql_admin_user",
                               "sql_server_port", "sql_sock"]
        if self.setting in parse_file_list:
            output = parse_file()
        elif self.setting in parse_failover_list:
            output = self.parse_failover()
        elif self.nosql is False:
            output = self.parse_sql_custom()
        else:
            self.error("all")
        if output is False:
            self.error("sql")
        return str(output)

    def error(self, parser_type):
        LogWrite("%s parser could not find setting %s" % (parser_type.capitalize(), self.setting))
        raise SystemExit("%s parser could not find setting %s" % (parser_type.capitalize(), self.setting))

    @lru_cache()
    def parse_sql(self, command=None):
        if command is not None:
            response = DoSql(command)
        else:
            response = DoSql("SELECT data FROM ga.Setting WHERE setting = '%s' and belonging = '%s';" % (self.setting, parse_file("hostname")))
        if response is False or response is None or response == "":
            self.error("sql")
        else:
            return response

    @lru_cache()
    def parse_sql_custom(self):
        command = ["SELECT", "data", "FROM ga.Setting WHERE"]
        custom = False
        if self.table is not None:
            if self.table == "group":
                command = ["SELECT", "gid", "FROM ga.Grouping WHERE"]
            elif self.table == "object":
                command = ["SELECT", "type", "FROM ga.Object WHERE"]
            elif self.table == "data":
                command = ["SELECT", "data", "FROM ga.Data WHERE"]
        if self.output is not None:
            command[1], custom = self.output, True
        if self.setting is not None:
            if self.table is not None:
                if self.table == "group":
                    command.append("type = '%s'" % self.setting)
                elif self.table == "object":
                    command.append("name = '%s'" % self.setting)
                elif self.table == "data":
                    command.append("agent = '%s'" % self.setting)
            else:
                command.append("setting = '%s'" % self.setting)
            custom = True
        if self.belonging is not None:
            if self.setting is not None:
                prefix = "AND"
            else:
                prefix = ""
            if self.table is not None:
                if self.table == "group":
                    insert = "member"
                elif self.table == "data":
                    insert = "agent"
            else:
                insert = "belonging"
            command[3], custom = "%s %s = '%s'" % (prefix, insert, self.belonging), True
        if self.filter is not None:
            command.append("AND %s" % self.filter)
            custom = True
        if custom is True:
            return self.parse_sql(' '.join(command) + ";")
        else:
            return self.parse_sql()

    @lru_cache()
    def parse_hardcoded(self):
        config_dict = {"path_log": "%s/log" % parse_file("path_root"), "path_backup": "%s/backup" % parse_file("path_root"), "sql_server_port": "3306"}
        if parse_file("setuptype") != "agent":
            config_server_dict = {"sql_server_ip": "127.0.0.1"}
            config_dict = {**config_dict, **config_server_dict}
        if self.setting in config_dict.keys():
            for key, value in config_dict.items():
                if key.find(self.setting) != -1:
                    return value
            return False
        else:
            return False

    def parse_failover(self):
        parse_sql_output = self.parse_sql()
        if parse_sql_output is False or parse_sql_output is None or parse_sql_output == "" or self.nosql is True:
            parse_file_output = parse_file(self.setting)
            if parse_file_output is False or parse_file_output is None or parse_file_output == "":
                if self.parse_hardcoded() is False:
                    self.error("all")
                else:
                    return self.parse_hardcoded()
            else:
                return parse_file_output
        else:
            return self.parse_sql()
