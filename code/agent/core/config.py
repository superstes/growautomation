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

from ga.core import owl
from ga.core import ant


class get(object):
    def __init__(self, setting, customtable=None, skipsql=False):
        self.setting = setting
        self.request = None
        self.table = customtable
        self.skipsql = skipsql
        self.start()

    def start(self, request=None):
        if self.request is None:
            self.setting = self.request
        parse_file_list = ["setuptype", ]
        parse_sql_list = ["backup", "backup_time", "backup_log", "log_level"]
        parse_failover_list = ["path_root", "hostname"]
        if self.request in parse_file_list:
            self.parse_file()
        elif self.request in parse_sql_list:
            self.parse_sql()
        elif self.request in parse_failover_list:
            self.parse_failover()
        else:
            self.parse_sql_custom()

    def error(self, parser_type):
        ant.log("%s parser could not find setting %s" % (parser_type.capitalize(), self.request))
        return SystemExit("%s parser could not find setting %s" % (parser_type.capitalize(), self.request))

    @lru_cache()
    def parse_file(self):
        response = ant.line("find", self.request).split("=")[1]
        if response is False or response is None or response == "":
            self.error("file")
        else:
            return response

    @lru_cache()
    def parse_sql(self):
        if self.start("setuptype") == "agent":
            response = owl.do("SELECT data FROM ga.AgentConfig WHERE setting = '%s' and agent = '%s';" % (self.request, self.start("hostname")))
        else:
            response = owl.do("SELECT data FROM ga.ServerConfig WHERE setting = '%s';" % self.request)
        if response is False or response is None or response == "":
            self.error("sql")

    @lru_cache()
    def parse_sql_custom(self):
        if self.table is None:
            self.parse_sql()
        else:
            if self.start("setuptype") == "agent":
                return owl.do("SELECT data FROM ga.%s WHERE setting = '%s' and agent = '%s';" % (self.table, self.request, self.start("hostname")))
            else:
                return owl.do("SELECT data FROM ga.%s WHERE setting = '%s';" % (self.table, self.request))

    def parse_hardcoded(self):
        config_dict = {"path_log": "%s/log" % self.start("path_root"), "path_backup": "%s/backup" % self.start("path_root")}
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


class path:
    root = ant.line("find", "garoot=", file="/etc/growautomation.version")[7:]
    try:
        log = owl.do(command("path_log"))
        backup = owl.do(command("path_backup"))
    except KeyError:
        log = "%s/log" % root
        backup = "%s/backup" % root


class mysql:
    server_port = ant.line("find", "serverport=")[11:]
    if server_port != "" and server_port is not None:
        server_port = 3306
    if setuptype == "agent":
        server_ip = ant.line("find", "serverip=")[9:]
        user = ant.line("find", "agentuser=")[10:]
        pwd = ant.line("find", "agentpassword=")[14:]
        localuser = ant.line("find", "localuser=")[10:]
        localpwd = ant.line("find", "localpassword=")[14:]
    else:
        server_ip = "127.0.0.1"
        user = ant.line("find", "serveruser=")[11:]
        pwd = ant.line("find", "serverpassword=")[15:]
        sock = owl.do(command("sql_sock"))




# class old:
    # will not be needed often -> should be queried manually if needed
    # namemaxletters = 10
    # namemaxnumbers = 100
    # sensortime = "10"		        #How often should the sensordata be written to the database (minutes)
    # sensorahtdisabled = "no"
    # sensorehdisabled = "no"
    # adcdisabled = ["adc02"]
    # adcconnected = {"adc01": "i2c-1", "adc02": "i2c-2"}
    # ahtadisabled = ["ahta02"]
    # ahtaconnected = {"ahta01": "26", "ahta02": "19"}
    # ehbdisabled = ["ehb02"]
    # ehbconnected = {"ehb01": {"adc01": "0"}, "ehb02": {"adc02": "1"}}
    # actiontypes = {"eh": ("pump", "win"), "aht": ("win")}
    # actionblock01 = {"sensor": {"eh": ("ehb01", "ehb02"), "aht": ("ahta01", "ahta02")}, "action": {"win": ("wina02")}}
    # actionblock02 = {"sensor": {"eh": ("ehb01", "ehb02")}, "action": {"pump": ("pumpa01", "pumpa04"), "win": ("wina01")}}
    # pumpdisabled = []
    # pumpconnected = ("pumpa01", "pumpa04")
    # pumpactivation = "60"		#The pump will be activated if the humidity falls under this value
    # pumptime = 10 #600		    #Runtime in seconds
    # windisabled = {}
    # winconnected = {"win01": {"fwd": "20", "rev": "21"}, "win02": {"fwd": "16", "rev": "12"}}
    # winopentime = 5
    # psua01password = "PASSWORD"
    # psua01ip = "IP"
    # psua01webport = 8080
    # psua01outlets = {"1": "pumpa01", "2": "pumpa02", "3": "pumpa03", "4": ""}
    # psua02password = "PASSWORD"
    # psua02ip = "IP"
    # psua02webport = 8080
    # psua02outlets = {"1": "pumpa04", "2": "", "3": "", "4": ""}