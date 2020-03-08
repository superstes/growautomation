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


class GetConfig(object):
    def __init__(self, setting, customtable=None, skipsql=False):
        self.setting = setting
        self.request = None
        self.table = customtable
        self.skipsql = skipsql
        self.file = "./core.conf"
        self.start()

    def start(self, request=None):
        if self.request is None:
            self.setting = self.request
        parse_file_list = ["setuptype", "sql_pwd", "sql_local_user", "sql_local_pwd", "sql_agent_pwd", "sql_admin_pwd"]
        parse_sql_list = ["backup", "backup_time", "backup_log", "log_level"]
        parse_failover_list = ["path_root", "hostname", "sql_server_port", "sql_server_ip", "sql_agent_user", "sql_admin_user",
                               "sql_server_port", "sql_sock"]
        if self.request in parse_file_list:
            self.parse_file()
        elif self.request in parse_sql_list:
            self.parse_sql()
        elif self.request in parse_failover_list:
            self.parse_failover()
        else:
            self.parse_sql_custom()

    def error(self, parser_type):
        LogWrite("%s parser could not find setting %s" % (parser_type.capitalize(), self.request))
        return SystemExit("%s parser could not find setting %s" % (parser_type.capitalize(), self.request))

    def parse_file_find(self):
        tmpfile = open(self.file, 'r')
        for xline in tmpfile.readlines():
            if xline.find(self.request) != -1:
                return xline
        return False

    @lru_cache()
    def parse_file(self):
        response = self.parse_file_find().split("=")[1]
        if response is False or response is None or response == "":
            self.error("file")
        else:
            return response

    @lru_cache()
    def parse_sql(self):
        if self.start("setuptype") == "agent":
            response = DoSql("SELECT data FROM ga.AgentConfig WHERE setting = '%s' and agent = '%s';" % (self.request, self.start("hostname")))
        else:
            response = DoSql("SELECT data FROM ga.ServerConfig WHERE setting = '%s';" % self.request)
        if response is False or response is None or response == "":
            self.error("sql")

    @lru_cache()
    def parse_sql_custom(self):
        if self.table is None:
            self.parse_sql()
        else:
            if self.start("setuptype") == "agent":
                return DoSql("SELECT data FROM ga.%s WHERE setting = '%s' and agent = '%s';" % (self.table, self.request, self.start("hostname")))
            else:
                return DoSql("SELECT data FROM ga.%s WHERE setting = '%s';" % (self.table, self.request))

    def parse_hardcoded(self):
        config_dict = {"path_log": "%s/log" % self.start("path_root"), "path_backup": "%s/backup" % self.start("path_root"), "sql_server_port": "3306"}
        if self.start("setuptype") != "agent":
            config_server_dict = {"sql_server_ip": "127.0.0.1"}
            config_dict = {**config_dict, **config_server_dict}
        if self.request in config_dict.keys():
            for key, value in config_dict.items():
                if key.find(self.request) != -1:
                    return value
            return False
        else:
            return False

    def parse_failover(self):
        if self.parse_sql() is False or self.parse_sql() is None or self.parse_sql() == "" or self.skipsql is True:
            if self.parse_file() is False or self.parse_file() is None or self.parse_file() == "":
                if self.parse_hardcoded() is False:
                    self.error("all")
                else:
                    self.parse_hardcoded()
            else:
                self.parse_file()
        else:
            self.parse_sql()
