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

#ga_version0.3

from functools import lru_cache

from ga.core.owl import DoSql
from ga.core.smallant import LogWrite
from ga.core.config_parser_file import GetConfig as parse_file


class GetConfig(object):
    def __init__(self, setting, customtable=None, skipsql=False):
        self.setting = setting
        self.table = customtable
        self.skipsql = skipsql

        self.start()

    def start(self, request=None):
        if request is None:
            request = self.setting

        parse_file_list = ["setuptype", "sql_pwd", "sql_local_user", "sql_local_pwd", "sql_agent_pwd", "sql_admin_pwd"]
        parse_sql_list = ["backup", "backup_time", "backup_log", "log_level"]
        parse_failover_list = ["path_root", "hostname", "sql_server_port", "sql_server_ip", "sql_agent_user", "sql_admin_user",
                               "sql_server_port", "sql_sock"]
        if request in parse_file_list:
            return parse_file(request)
        elif request in parse_sql_list:
            return self.parse_sql(request)
        elif request in parse_failover_list:
            return self.parse_failover(request)
        else:
            return self.parse_sql_custom(request)

    def error(self, request, parser_type):
        LogWrite("%s parser could not find setting %s" % (parser_type.capitalize(), request))
        raise SystemExit("%s parser could not find setting %s" % (parser_type.capitalize(), request))

    @lru_cache()
    def parse_sql(self, request):
        if self.start("setuptype") == "agent":
            response = DoSql("SELECT data FROM ga.AgentConfig WHERE setting = '%s' and agent = '%s';" % (request, self.start("hostname")))
        else:
            response = DoSql("SELECT data FROM ga.ServerConfig WHERE setting = '%s';" % request)
        if response is False or response is None or response == "":
            self.error("sql", request)
        else:
            return response

    @lru_cache()
    def parse_sql_custom(self, request):
        if self.table is None:
            self.parse_sql(request)
        else:
            if self.start("setuptype") == "agent":
                return DoSql("SELECT data FROM ga.%s WHERE setting = '%s' and agent = '%s';" % (self.table, request, self.start("hostname")))
            else:
                return DoSql("SELECT data FROM ga.%s WHERE setting = '%s';" % (self.table, request))

    def parse_hardcoded(self, request):
        config_dict = {"path_log": "%s/log" % self.start("path_root"), "path_backup": "%s/backup" % self.start("path_root"), "sql_server_port": "3306"}
        if self.start("setuptype") != "agent":
            config_server_dict = {"sql_server_ip": "127.0.0.1"}
            config_dict = {**config_dict, **config_server_dict}
        if request in config_dict.keys():
            for key, value in config_dict.items():
                if key.find(request) != -1:
                    return value
            return False
        else:
            return False

    def parse_failover(self, request):
        parse_sql_output = self.parse_sql(request)
        if parse_sql_output is False or parse_sql_output is None or parse_sql_output == "" or self.skipsql is True:
            parse_file_output = parse_file(request)
            if parse_file_output is False or parse_file_output is None or parse_file_output == "":
                if self.parse_hardcoded(request) is False:
                    self.error("all", request)
                else:
                    return self.parse_hardcoded(request)
            else:
                return parse_file_output
        else:
            return self.parse_sql(request)
