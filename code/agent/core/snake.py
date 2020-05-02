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
# sensor master module

from .config import Config
from .owl import DoSql
from .ant import LogWrite
from .smallant import debugger
from .smallant import share

from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe
from sys import argv as sys_argv
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
import signal
from time import sleep as time_sleep

LogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), level=2)


class Balrog:
    def __init__(self, sensor):
        self.sensor, self.own_dt = sensor, None
        self.processed_list, self.lock_list = [], []
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
        self.sensor_type = True if self.sensor in Config(output="name", table="object", filter="class = 'sensor'").get("list") else False
        self.devicetype() if self.sensor_type is True else self.device(self.sensor)

    def devicetype(self):
        device_list, self.own_dt = [], self.sensor
        # check all for loops if they will break if only one element is in list -> find clean solution
        for device in Config(output="name", table="object", filter="class = '%s'" % self.sensor).get("list"):
            if not Config(setting="timer", belonging=device, empty=True).get() and Config(setting="enabled", belonging=device).get() == "1":
                device_list.append(device)
        for device in device_list:
            if device in self.processed_list: continue
            else: self.device(device)
        # ask for threading support when sensor-functions are added

    def device(self, device):
        self.own_dt = Config(output="class", table="object", setting=device).get()
        # if device => self.sensor doesn't need to check if enabled since it was already checked when accepting the timer
        connection = Config(setting="connection", belonging=device).get()
        if connection == "direct":
            output = self.start(device)
            debugger("snake - device |direct |output '%s'" % output)
            self.write_data(device, output)
        elif connection == "downlink": self.downlink(device, Config(setting="downlink", belonging=device).get())
        else:
            debugger("snake - device |%s has no connection configured" % device)
            LogWrite("Device %s has no acceptable connection configured" % device, level=1)
            return False

    def downlink(self, device, downlink):
        if Config(setting="enabled", belonging=downlink).get() != "1": return False
        devicetype = Config(output="class", table="object", setting=downlink).get()
        if Config(setting="enabled", belonging=devicetype).get() != "1": return False
        type_opp = Config(setting="output_per_port", belonging=devicetype).get()

        def get_setting_dict():
            type_setting, setting = Config(output="setting,data", belonging=devicetype).get(), Config(output="setting,data", belonging=downlink).get()
            setting_dict, type_setting_dict = {}, {}
            for setting, data in setting: setting_dict[setting] = data
            for setting, data in type_setting:
                if setting not in setting_dict.keys(): setting_dict[setting] = data
            debugger("snake - downlink |get_setting_dict |output '%s'" % setting_dict)
            return setting_dict

        if type_opp == "1":
            sensor_dict = {device: Config(setting="port", belonging=device).get()}
            debugger("snake - downlink |opp 1 |input '%s'" % sensor_dict)
            output = self.start(downlink, device_mapping_dict=sensor_dict, setting_dict=get_setting_dict())
            debugger("snake - downlink |opp 1 |output '%s'" % output)
            self.write_data(device, output)
        elif type_opp == "0":
            portcount = Config(setting="portcount", belonging=downlink).get()
            if self.sensor_type:
                sensor_list, sensor_dict = Config(output="name", setting="downlink", filter="data = '%s'" % downlink).get(), {}
                for sensor in sensor_list:
                    if Config(output="class", table="object", setting=sensor).get() == self.sensor:
                        if sensor in self.processed_list or Config(setting="enabled", belonging=sensor).get() != "1": continue
                        sensor_dict[sensor] = Config(setting="port", belonging=sensor).get()
            else:
                sensor_dict = {device: Config(setting="port", belonging=device).get()}
            if len(sensor_dict.keys()) < portcount:
                for i in range(portcount):
                    if i not in sensor_dict.values():
                        sensor_dict["dummy_%s" % i] = i
                        # portlist in dict will start at 0 => throw it into the docs
                sensor_dict = {key: value for key, value in sorted(sensor_dict.items(), key=lambda item: item[1])}
            debugger("snake - downlink |opp 0 |input '%s'" % sensor_dict)
            output_dict = self.start(downlink, device_mapping_dict=sensor_dict, setting_dict=get_setting_dict())
            debugger("snake - downlink |opp 0 |output '%s'" % output_dict)
            for sensor, data in output_dict.items():
                if sensor in self.processed_list: self.write_data(sensor, data)
            # if opp -> output must be string
            # if not opp -> output must be dict with sensor as key and data as value
        else: return False

    def start(self, device, device_mapping_dict=None, setting_dict=None):
        if device_mapping_dict is None: self.processed_list.extend(device)
        else:
            for device in device_mapping_dict.keys():
                if device.find("dummy") == -1: self.processed_list.append(device)
        self.lock(device)
        function = Config(setting="function", belonging=self.own_dt).get()
        custom_arg = Config(setting="function_arg", belonging=self.own_dt, empty=True).get()
        if not custom_arg: custom_arg = None
        port = Config(setting="port", belonging=device).get()
        devicetype_class = Config(output="class", table="object", setting=self.own_dt).get()

        function_path = "%s/%s/%s" % (Config(setting="path_root").get(), devicetype_class, function)
        LogWrite("Starting function %s for device %s.\nInput data:\nDevice mapping '%s'\nSettings '%s'" %
                 (function_path, device, device_mapping_dict, setting_dict), level=4)
        debugger("snake - start |/usr/bin/python3 %s %s %s %s %s" %
                 (function_path, port, device_mapping_dict, setting_dict, custom_arg))
        output, error = subprocess_popen(["/usr/bin/python3 %s %s %s %s %s" %
                                          (function_path, port, device_mapping_dict, setting_dict, custom_arg)],
                                         shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
        output_str, error_str = output.decode("ascii").strip(), error.decode("ascii").strip()

        LogWrite("Function '%s' was processed for device %s.\nOutput '%s'" % (function_path, device, output_str), level=3)
        debugger("snake - start |output by processing %s '%s'" % (device, output_str))
        if error_str != "":
            LogWrite("Error by executing %s:\n'%s'" % (device, error_str), level=2)
            debugger("snake - start |error by executing %s '%s'" % (device, error_str))
        if device_mapping_dict is None: return output_str
        else: return dict(output_str)

    def lock(self, device):
        try_count, wait_time, max_try_count = 1, 10, 31
        # note: set config for wait time and timeout in db belonging to sensor_master
        while True:
            if share(action="get", name="lock_%s" % device, outtypK="int") == 1: time_sleep(wait_time)
            else: break
            if try_count > max_try_count:
                debugger("snake - lock |device %s reached max retries -> giving up to get lock" % device)
                LogWrite("Unable to get lock for device '%s' in time. Timeout (%s sec) reached." % (device, wait_time * try_count), level=2)
                return False
            debugger("snake - lock |device %s waiting for lock for % seconds" % (device, wait_time * try_count))
            try_count += 1
        try_count -= 1
        share(action="set", name="lock_%s" % device, data=1)
        self.lock_list.append(device)
        debugger("snake - lock |device %s locked" % device)
        LogWrite("Locked device '%s' (waited for ~%s sec)." % (device, wait_time * try_count), level=2)
        return True

    def unlock(self, device):
        share(action="set", name="lock_%s" % device, data=0)
        self.lock_list.remove(device)
        debugger("snake - unlock |device %s unlocked" % device)
        LogWrite("Unlocked device '%s'." % device, level=2)
        return True

    def write_data(self, device, data):
        sql = DoSql("INSERT INTO ga.Data (agent,data,device) VALUES ('%s','%s','%s');" % (Config("hostname").get(), data, device), write=True).start()
        LogWrite("Wrote data for device '%s' to database. Output: %s" % (device, sql), level=4)
        return sql

    def stop(self, signum=None, stack=None):
        if signum is not None:
            debugger("snake - stop |got signal %s" % signum)
            LogWrite("Sensor master received signal %s" % signum, level=2)
        if len(self.lock_list) > 0:
            unlock_list = self.lock_list
            for device in unlock_list: self.unlock(device)
            debugger("snake - stop |unlocked following devices '%s'" % unlock_list)
        debugger("snake - stop |exiting")
        raise SystemExit


try: Balrog(sys_argv[1])
except IndexError:
    LogWrite("No sensor provided. Exiting.")
    raise SystemExit
