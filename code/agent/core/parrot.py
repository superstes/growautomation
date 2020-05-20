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

# ga_version 0.4
# check module

from core.config import Config
from core.smallant import Log
from core.ant import time_subtract
from core.smallant import debugger
from core.smallant import VarHandler
from core.smallant import process

from time import sleep
from sys import argv as sys_argv
from sys import exc_info as sys_exc_info
import signal


def _signal_handler(signum=None, stack=None):
    # get list of memory-vars added -> Varhandler("peritem").clean()
    # clean other stuff ..
    raise SystemExit("Received signal %s - '%s'" % (signum, sys_exc_info()[0].__name__))


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


class ActionLoader:
    def __init__(self, device_type, device_sector_dict):
        self.device_sector_dict, self.type = device_sector_dict, device_type
        self.device_setting_dict = None

    def __repr__(self):
        for device in self.device_sector_dict.keys():
            device_type_setting = Config(output="setting,data", belonging=self.type).get()
            device_setting = Config(output="setting,data", belonging=device).get()
            device_setting.extend(y for y in device_type_setting if y not in device_setting)
            self.device_setting_dict = {device: device_setting}
        self.action_prequesits()

    def action_prequesits(self):
        function = Config(setting='function', belonging=self.type).get()
        self.action_start(function, boomerang=True) if Config(setting='boomerang', belonging=self.type).get() == 'True' else self.action_start(function)

    def action_start(self, function, boomerang=False):
        command = "/usr/bin/python3 %s/action/%s %s" % (Config('path_root').get(), function, self.device_setting_dict)
        if boomerang is True:
            time_wait = Config('time_wait', 'AgentConfigDeviceTypeSetting', CustomAnd=self.type).get()
            output1, error1 = process(command + ' start', out_error=True)
            sleep(time_wait)
            output2, error2 = process(command + ' stop', out_error=True)
            Log("Function %s called as boomerang.\nStart error:\n%s\nStop error:\n%s" % (function, error1, error2), level=2).write()
            Log("Start output:\n%s\nStop output:\n%s" % (output1, output2), level=3).write()
        else:
            output, error = process(command, out_error=True)
            Log("Function %s called.\nError:\n%s" % (function, error), level=2).write()
            Log("Output:\n%s" % output, level=3).write()


class SectorCheck:
    def __init__(self, sector_dict):
        self.sector_list = list(sector_dict.keys())
        self.type = list(sector_dict.values())[0]

    def __repr__(self):
        self.check_type_links()

    def check_type_links(self):
        link_exist_list = Config(setting='link', table='member').get()
        link_inuse_list = Config(setting='link', belonging=self.type, table='member').get()
        [self.check_action_sector(link) for link in link_inuse_list if link in link_exist_list]

    def check_action_sector(self, link):
        device_type_list = Config(setting='link', filter="gid = '%s'" % link, table='member').get()
        [device_type_list.remove(device) for device in reversed(device_type_list) if Config(setting=device, table='object').get() != 'action']
        for device_type in device_type_list:
            if Config(setting='enabled', belonging=device_type).get() != '1':
                device_type_list.remove(device_type)
                Log("Action %s is disabled." % device_type, level=2).write()
                continue
            device_list, device_sector_dict = Config(filter="class = '%s'" % device_type, table='object').get(), {}
            [device_list.remove(device) for device in reversed(device_list) if Config(setting='enabled', belonging=device).get() != '1']
            for device in device_list: device_sector_dict[device] = Config(setting='sector', belonging=device, table='member').get()
            for device, sector in device_sector_dict.items():
                sector_list = self.check_device_sector(sector)
                if sector_list is False:
                    Log("Device %s is in none of the following sectors: %s" % (device, self.sector_list), level=3).write()
                    del device_sector_dict[device]
                    continue
                device_sector_dict[device] = sector_list
            ActionLoader(device_type, device_sector_dict)

    def check_device_sector(self, value: str):
        value_sector_list, output_list = [], []
        value_sector_list.append(value.split(",")) if value.find(",") != -1 else value_sector_list.append(value)
        [output_list.append(sector) for sector in self.sector_list if sector in value_sector_list]
        return output_list if len(output_list) > 0 else False


class ThresholdCheck:
    def __init__(self, sensor):
        self.sensor = sensor
        self.check_range = None

    def __repr__(self):
        # checks only devicetypes
        # will check if input is sensor or type
        if Config(setting=self.sensor, table='object').get() == 'sensor':
            if Config(setting='enabled', belonging=self.sensor).get() == '1':
                threshold = Config(setting='threshold', belonging=self.sensor).get()
                for sector in self.get_sector_list():
                    average_data_list = []
                    for device, device_sector in self.get_device_dict().items():
                        if self.check_device_sector(device_sector, sector) is True:
                            average_data = self.get_average_data(device)
                            average_data_list.append(average_data)
                            Log("Device %s in sector %s.\nAverage data: %s" % (device, sector, average_data), level=3).write()
                        else:
                            Log("Device %s not in sector %s." % (device, sector), level=3).write()
                            continue
                    sector_average = sum(average_data_list) / len(average_data_list)
                    if sector_average >= threshold:
                        Log("DeviceType %s did exceed it's threshold in sector %s. (%s/%s)\nStarting SectorCheck."
                            % (self.sensor, sector, sector_average, threshold), level=2).write()
                        sector_dict = {sector: self.sensor}
                    else:
                        Log("DeviceType %s did not exceed it's threshold in sector %s. (%s/%s)"
                            % (self.sensor, sector, sector_average, threshold), level=2).write()
                        continue
                SectorCheck(sector_dict)

    def input_device(self):
        print('no')

    def input_devicetype(self):
        print('no')

    def get_device_dict(self):
        device_list = Config(filter="class = '%s'" % self.sensor, table='object').get()
        for device in device_list:
            if Config(setting='enabled', belonging=device).get() == '1':
                device_dict = {device: Config(setting='sector', belonging=device, table='member').get()}
            else:
                Log("Device %s is disabled." % device, level=3).write()
                continue
        return device_dict

    def get_sector_list(self):
        sector_inuse_list, sector_list, sector_exist_list = [], [], Config(setting='sector', table='member').get()
        for sector in self.get_device_dict().values():
            sector_inuse_list.append(sector.split(",")) if sector.find(",") != -1 else sector_inuse_list.append(sector)
        [sector_list.append(sector) for sector in sector_inuse_list if sector in sector_exist_list]
        return sector_list

    def get_data(self, device):
        if self.check_range is None:
            self.check_range = int(Config(setting='range', belonging='check').get())
        time_now, time_before = time_subtract(int(Config(setting='timer', belonging=self.sensor).get()) * self.check_range, both=True)
        return Config(table='data', belonging=device, filter="changed => '%s' AND changed <= '%s' AND device = '%s'" % (time_now, time_before, device)).get()

    def get_average_data(self, device):
        if type(device) == 'list':
            data_list = []
            [data_list.append(self.get_data(device)) for device in device]
        elif type(device) == 'str': data_list = self.get_data(device)
        else: return False
        return sum(data_list) / len(data_list)

    def check_device_sector(self, value, sector):
        value_sector_list = []
        value_sector_list.append(value.split(",")) if value.find(",") != -1 else value_sector_list.append(value)
        return True if sector in value_sector_list else False


try: ThresholdCheck(sys_argv[1])
except IndexError:
    Log('No sensor provided. Exiting.').write()
    raise SystemExit

