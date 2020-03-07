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

from ga import owl
from ga import ant

hostname = ant.line("find", "name=")[6:]
setuptype = ant.line("find", "type=")[6:]


def command(setting):
    if setuptype == "agent":
        return "SELECT data FROM ga.AgentConfig WHERE setting = '%s' and agent = '%s';" % (setting, hostname)
    else:
        return "SELECT data FROM ga.ServerConfig WHERE setting = '%s';" % setting


class path:
    root = ant.line("find", "garoot=", file="/etc/growautomation.version")[8:]
    try:
        log = owl.do(command("path_log"))
        backup = owl.do(command("path_backup"))
    except KeyError:
        log = "%s/log" % root
        backup = "%s/backup" % root


class mysql:
    server_port = ant.line("find", "serverport=")[12:]
    if server_port != "" and server_port is not None:
        server_port = 3306
    if setuptype == "agent":
        server_ip = ant.line("find", "serverip=")[10:]
        user = ant.line("find", "agentuser=")[11:]
        pwd = ant.line("find", "agentpassword=")[15:]
        localuser = ant.line("find", "localuser=")[11:]
        localpwd = ant.line("find", "localpassword=")[15:]
    else:
        server_ip = "127.0.0.1"
        user = ant.line("find", "serveruser=")[12:]
        pwd = ant.line("find", "serverpassword=")[16:]
        sock = owl.do(command("sql_sock"))


class core:
    backup = owl.do(command("backup"))
    if backup is True:
        backup_time = owl.do(command("backup_time"))
        backup_log = owl.do(command("backup_log"))
        loglevel = owl.do(command("log_level"))


def query(setting, customtable=None):
    if customtable is not None:
        table = customtable
    if setuptype == "agent":
        return owl.do("SELECT data FROM ga.%s WHERE setting = '%s' and agent = '%s';" % (table, setting, hostname))
    else:
        return owl.do("SELECT data FROM ga.%s WHERE setting = '%s';" % (table, setting))

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