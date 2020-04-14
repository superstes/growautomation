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

# ga_version 0.3

from ga.core.config import GetConfig
from ga.core.ant import LogWrite
from ga.core.ant import time_subtract

from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from time import sleep
from sys import argv as sys_argv
import signal


LogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), level=2)


class ActionLoader:
    def __init__(self, device_type, device_sector_dict, debug=False):
        self.device_sector_dict = device_sector_dict
        self.type = device_type
        self.device_setting_dict = None
        self.debug = debug

    def __repr__(self):
        for device in self.device_sector_dict.keys():
            device_type_setting = GetConfig(output="setting,data", belonging=self.type)
            device_setting = GetConfig(output="setting,data", belonging=device)
            device_setting.extend(y for y in device_type_setting if y not in device_setting)
            self.device_setting_dict = {device: device_setting}
        self.action_prequesits()

    def action_prequesits(self):
        function = GetConfig(setting="function", belonging=self.type)
        self.action_start(function, boomerang=True) if GetConfig(setting="boomerang", belonging=self.type) == "True" else self.action_start(function)

    def action_start(self, function, boomerang=False):
        command = "/usr/bin/python3 %s/action/%s %s" % (GetConfig("path_root"), function, self.device_setting_dict)

        def start(DoIt):
            return subprocess_popen([DoIt], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
        if boomerang is True:
            time_wait = GetConfig("time_wait", "AgentConfigDeviceTypeSetting", CustomAnd=self.type)
            output1, error1 = start(command + " start")
            sleep(time_wait)
            output2, error2 = start(command + " stop")
            LogWrite("Function %s called as boomerang.\nStart error:\n%s\nStop error:\n%s" % (function, error1, error2), level=2)
            LogWrite("Start output:\n%s\nStop output:\n%s" % (output1, output2), level=3)
        else:
            output, error = start(command)
            LogWrite("Function %s called.\nError:\n%s" % (function, error), level=2)
            LogWrite("Output:\n%s" % output, level=3)


class SectorCheck:
    def __init__(self, sector_dict, debug=False):
        self.sector_list = list(sector_dict.keys())
        self.type = list(sector_dict.values())[0]
        self.debug = debug

    def __repr__(self):
        self.check_type_links()

    def check_type_links(self):
        link_exist_list = GetConfig(setting="link", table="group")
        link_inuse_list = GetConfig(setting="link", belonging=self.type, table="group")
        [self.check_action_sector(link) for link in link_inuse_list if link in link_exist_list]

    def check_action_sector(self, link):
        device_type_list = GetConfig(setting="link", filter="gid = '%s'" % link, table="group")
        [device_type_list.remove(device) for device in reversed(device_type_list) if GetConfig(setting=device, table="object") != "action"]
        for device_type in device_type_list:
            if GetConfig(setting="enabled", belonging=device_type) != "1":
                device_type_list.remove(device_type)
                LogWrite("Action %s is disabled." % device_type, level=2)
                continue
            device_list = GetConfig(filter="class = '%s'" % device_type, table="object")
            [device_list.remove(device) for device in reversed(device_list) if GetConfig(setting="enabled", belonging=device) != "1"]
            for device in device_list: device_sector_dict = {device: GetConfig(setting="sector", belonging=device, table="group")}
            for device, sector in device_sector_dict.items():
                sector_list = self.check_device_sector(sector)
                if sector_list is False:
                    LogWrite("Device %s is in none of the following sectors: %s" % (device, self.sector_list), level=3)
                    del device_sector_dict[device]
                    continue
                device_sector_dict[device] = sector_list
            ActionLoader(device_type, device_sector_dict, self.debug)

    def check_device_sector(self, value):
        value_sector_list, output_list = [], []
        value_sector_list.append(value.split(",")) if value.find(",") != -1 else value_sector_list.append(value)
        [output_list.append(sector) for sector in self.sector_list if sector in value_sector_list]
        return output_list if len(output_list) > 0 else False


class ThresholdCheck:
    def __init__(self, sensor, debug=False):
        self.sensor = sensor
        self.check_range = None
        self.debug = debug

    def __repr__(self):
        # checks only devicetypes
        # will check if input is sensor or type
        if GetConfig(setting=self.type, table="object") == "sensor":
            if GetConfig(setting="enabled", belonging=self.type) == "1":
                threshold = GetConfig(setting="threshold", belonging=self.type)
                for sector in self.get_sector_list():
                    average_data_list = []
                    for device, device_sector in self.get_device_dict().items():
                        if self.check_device_sector(device_sector, sector) is True:
                            average_data = self.get_average_data(device)
                            average_data_list.append(average_data)
                            LogWrite("Device %s in sector %s.\nAverage data: %s" % (device, sector, average_data), level=3)
                        else:
                            LogWrite("Device %s not in sector %s." % (device, sector), level=3)
                            continue
                    sector_average = sum(average_data_list) / len(average_data_list)
                    if sector_average >= threshold:
                        LogWrite("DeviceType %s did exceed it's threshold in sector %s. (%s/%s)\nStarting SectorCheck." % (self.type, sector, sector_average, threshold), level=2)
                        sector_dict = {sector: self.type}
                    else:
                        LogWrite("DeviceType %s did not exceed it's threshold in sector %s. (%s/%s)" % (self.type, sector, sector_average, threshold), level=2)
                        continue
                SectorCheck(sector_dict, self.debug)

    def input_device(self):
        # if input = device

    def input_devicetype(self):
        # if input = type

    def get_device_dict(self):
        device_list = GetConfig(filter="class = '%s'" % self.type, table="object")
        for device in device_list:
            if GetConfig(setting="enabled", belonging=device) == "1": device_dict = {device: GetConfig(setting="sector", belonging=device, table="group")}
            else:
                LogWrite("Device %s is disabled." % device, level=3)
                continue
        return device_dict

    def get_sector_list(self):
        sector_inuse_list, sector_list, sector_exist_list = [], [], GetConfig(setting="sector", table="group")
        for sector in self.get_device_dict().values():
            sector_inuse_list.append(sector.split(",")) if sector.find(",") != -1 else sector_inuse_list.append(sector)
        [sector_list.append(sector) for sector in sector_inuse_list if sector in sector_exist_list]
        return sector_list

    def get_data(self, device):
        if self.check_range is None:
            self.check_range = int(GetConfig(setting="range", belonging="check"))
        time_now, time_before = time_subtract(int(GetConfig(setting="timer", belonging=self.type)) * self.check_range, both=True)
        return GetConfig(table="data", belonging=device, filter="changed => '%s' AND changed <= '%s' AND device = '%s'" % (time_now, time_before, device))

    def get_average_data(self, device):
        if type(device) == "list":
            data_list = []
            [data_list.append(self.get_data(device)) for device in device]
        elif type(device) == "str": data_list = self.get_data(device)
        else: return False
        return sum(data_list) / len(data_list)

    def check_device_sector(self, value, sector):
        value_sector_list = []
        value_sector_list.append(value.split(",")) if value.find(",") != -1 else value_sector_list.append(value)
        return True if sector in value_sector_list else False


try:
    try:
        ThresholdCheck(sys_argv[1], debug=True) if sys_argv[2] == "True" else ThresholdCheck(sys_argv[1])
    except IndexError:
        ThresholdCheck(sys_argv[1])
except IndexError:
    LogWrite("No sensor provided. Exiting.")
    raise SystemExit

# to do
# check how to implement signal handling regarding multiple classes
# signal.signal(signal.SIGTERM, self.stop)
# signal.signal(signal.SIGINT, self.stop)