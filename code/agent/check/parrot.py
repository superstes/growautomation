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

from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from time import sleep

from ga.core.owl import DoSql
from ga.core.config import GetConfig
from ga.core.ant import LogWrite
from ga.core.ant import time_subtract


def LocalLogWrite(log, loglevel):
    LogWrite(log, "check", loglevel)


def query(command):
    output = DoSql(command)
    if output is False:
        LocalLogWrite("No data received from query %s." % command, loglevel=3)
    return output


LocalLogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), loglevel=2)


class ActionLoader:
    def __init__(self, device_type, device_sector_dict):
        self.device_sector_dict = device_sector_dict
        self.type = device_type
        self.device_setting_dict = None

    def __repr__(self):
        for device in self.device_sector_dict.keys():
            device_type_setting = query("SELECT setting,data FROM AgentConfigDeviceTypeSetting WHERE type = '%s';" % self.type)
            device_setting = query("SELECT setting,data FROM AgentConfigDeviceTypeSetting WHERE device = '%s';" % device)
            device_setting.extend(y for y in device_type_setting if y not in device_setting)
            self.device_setting_dict = {device: device_setting}
        self.action_prequesits()

    def action_prequesits(self):
        function = GetConfig("function", "AgentConfigDeviceTypeSetting", CustomAnd=self.type)
        if GetConfig("boomerang", "AgentConfigDeviceTypeSetting", CustomAnd=self.type) == "True":
            self.action_start(function, boomerang=True)
        else:
            self.action_start(function)

    def action_start(self, function, boomerang=False):
        command = "/usr/bin/python3 %s/action/%s %s" % (GetConfig("path_root"), function, self.device_setting_dict)

        def start(DoIt):
            return subprocess_popen([DoIt], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
        if boomerang is True:
            time_wait = GetConfig("time_wait", "AgentConfigDeviceTypeSetting", CustomAnd=self.type)
            output1, error1 = start(command + " start")
            sleep(time_wait)
            output2, error2 = start(command + " stop")
            LocalLogWrite("Function %s called as boomerang.\nStart error:\n%s\nStop error:\n%s" % (function, error1, error2), loglevel=2)
            LocalLogWrite("Start output:\n%s\nStop output:\n%s" % (output1, output2), loglevel=3)
        else:
            output, error = start(command)
            LocalLogWrite("Function %s called.\nError:\n%s" % (function, error), loglevel=2)
            LocalLogWrite("Output:\n%s" % output, loglevel=3)


class SectorCheck:
    def __init__(self, sector_dict):
        self.sector_list = list(sector_dict.keys())
        self.type = list(sector_dict.values())[0]

    def __repr__(self):
        link_exist_list = query("SELECT id FROM AgentConfigLink;")
        link_inuse_list = query("SELECT link FROM AgentConfigLinkSetting WHERE type = '%s';" % self.type)
        for link in link_inuse_list:
            if link in link_exist_list:
                self.check_action_sector(link)

    def check_action_sector(self, link):
        device_type_list = query("SELECT AgentConfigDeviceType.type FROM AgentConfigDeviceType INNER JOIN AgentConfigLinkSetting ON AgentConfigLinkSetting.type = AgentConfigDeviceType.type "
                                 "WHERE AgentConfigDeviceType.category = 'action' AND AgentConfigLinkSetting.link = '%s';" % link)
        for device_type in device_type_list:
            if GetConfig("enabled", "AgentConfigDeviceTypeSetting", CustomAnd=device_type) != "1":
                device_type_list.remove(device_type)
                LocalLogWrite("Action %s is disabled." % device_type)
                pass
            device_list = query("SELECT AgentConfigDevice.device FROM AgentConfigDevice INNER JOIN AgentConfigDeviceSetting ON AgentConfigDevice.device = AgentConfigDeviceSetting.device "
                                "WHERE AgentConfigDevice.type = '%s' AND AgentConfigDeviceSetting.setting = 'enabled' AND AgentConfigDeviceSetting.data = '1';" % device_type)
            for device in device_list:
                device_sector_dict = {device: query("SELECT AgentConfigDeviceSetting.data FROM AgentConfigDevice INNER JOIN AgentConfigDeviceSetting ON AgentConfigDevice.device = "
                                                    "AgentConfigDeviceSetting.device WHERE AgentConfigDeviceSetting.setting = 'sectors' AND AgentConfigDevice.device = '%s';" % device)}
            for device, sector in device_sector_dict.items():
                sector_list = self.check_device_sector(sector)
                if sector_list is False:
                    LocalLogWrite("Device %s is in none of the following sectors: %s" % (device, self.sector_list), loglevel=3)
                    del device_sector_dict[device]
                    pass
                device_sector_dict[device] = sector_list
            ActionLoader(device_type, device_sector_dict)

    def check_device_sector(self, value):
        value_sector_list = []
        if value.find(",") != -1:
            value_sector_list.append(value.split(","))
        else:
            value_sector_list.append(value)
        output_list = []
        for sector in self.sector_list:
            if sector in value_sector_list:
                output_list.append(sector)
        if len(output_list) > 0:
            return output_list
        else:
            return False


class ThresholdCheck:
    def __init__(self, input_type):
        self.type = input_type

    def __repr__(self):
        if query("SELECT category FROM ga.AgentConfigDeviceType WHERE type = '%s'" % self.type) == "sensor":
            if GetConfig("enabled", "AgentConfigDeviceTypeSetting", CustomAnd=self.type) == "True":
                threshold = GetConfig("threshold", "AgentConfigDeviceTypeSetting", CustomAnd=self.type)
                for sector in self.get_sector_list():
                    average_data_list = []
                    for device, device_sector in self.get_device_dict().items():
                        if self.check_device_sector(device_sector, sector) is True:
                            average_data = self.get_average_data(device)
                            average_data_list.append(average_data)
                            LocalLogWrite("Device %s in sector %s.\nAverage data: %s" % (device, sector, average_data), loglevel=3)
                        else:
                            LocalLogWrite("Device %s not in sector %s." % (device, sector), loglevel=3)
                            pass
                    sector_average = sum(average_data_list) / len(average_data_list)
                    if sector_average >= threshold:
                        LocalLogWrite("DeviceType %s did exceed it's threshold in sector %s. (%s/%s)\nStarting SectorCheck." % (self.type, sector, sector_average, threshold), loglevel=2)
                        sector_dict = {sector: self.type}
                    else:
                        LocalLogWrite("DeviceType %s did not exceed it's threshold in sector %s. (%s/%s)" % (self.type, sector, sector_average, threshold), loglevel=2)
                        pass
                SectorCheck(sector_dict)

    def get_device_dict(self):
        device_list = query("SELECT AgentConfigDevice.device FROM AgentConfigDevice INNER JOIN AgentConfigDeviceType ON AgentConfigDevice.type = AgentConfigDeviceType.type WHERE "
                            "AgentConfigDeviceType.type = '%s';" % self.type)
        for device in device_list:
            if query("SELECT data FROM AgentConfigDeviceSetting WHERE device = '%s' AND setting = 'enabled';" % device) == "1":
                device_dict = {device: query("SELECT data FROM AgentConfigDeviceSetting WHERE device = '%s' AND setting = 'sectors';")}
            else:
                LocalLogWrite("Device %s is disabled." % device, loglevel=3)
                pass
        return device_dict

    def get_sector_list(self):
        sector_exist_list = query("SELECT id FROM AgentConfigSector;")
        sector_inuse_list = []
        for sector in self.get_device_dict().values():
            if sector.find(",") != -1:
                sector_inuse_list.append(sector.split(","))
            else:
                sector_inuse_list.append(sector)
        sector_list = []
        for sector in sector_inuse_list:
            if sector in sector_exist_list:
                sector_list.append(sector)
        return sector_list

    def get_data(self, device):
        time_now, time_before = time_subtract(GetConfig("time_check", "AgentConfigDeviceTypeSetting", CustomAnd=self.type), both=True)
        return query("SELECT data FROM ga.AgentData WHERE changed => '%s' AND changed <= '%s' AND device = '%s';" % (time_now, time_before, device))

    def get_average_data(self, device):
        if type(device) == "list":
            data_list = []
            for device in device:
                data_list.append(self.get_data(device))
        elif type(device) == "str":
            data_list = self.get_data(device)
        else:
            return False
        return sum(data_list) / len(data_list)

    def check_device_sector(self, value, sector):
        value_sector_list = []
        if value.find(",") != -1:
            value_sector_list.append(value.split(","))
        else:
            value_sector_list.append(value)
        if sector in value_sector_list:
            return True
        else:
            return False
