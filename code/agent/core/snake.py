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
#     E-Mail: contact@growautomation.at
#     Web: https://git.growautomation.at

# ga_version 0.4
# sensor master module

from core.config import Config
from core.owl import DoSql
from core.smallant import Log
from core.smallant import debugger
from core.smallant import VarHandler
from core.smallant import process

from time import sleep as time_sleep
from time import perf_counter as time_counter
from sys import argv as sys_argv


class Balrog:
    def __init__(self, sensor):
        self.sensor, self.own_dt = sensor, None
        self.processed_list, self.lock_list = [], []
        self.sensor_type = ''

    def start(self):
        debugger("snake - init - input |sensor '%s'" % self.sensor)
        self.sensor = self.sensor.replace('sensor_', '')
        if self.sensor in Config(output='name', table='object', filter="class = 'sensor'").get('list'):
            self.sensor_type = True
        else: self.sensor_type = False
        if self.sensor_type is True:
            self._devicetype()
        else: self._device(self.sensor)

    def _devicetype(self):
        device_list, self.own_dt = [], self.sensor
        # check all for loops if they will break if only one element is in list -> find clean solution
        for device in Config(output='name', table='object', filter="class = '%s'" % self.sensor).get('list'):
            if not Config(setting='timer', belonging=device, empty=True).get() and Config(setting='enabled',
                                                                                          belonging=device).get() == '1':
                device_list.append(device)
        for device in device_list:
            if device in self.processed_list: continue
            else: self._device(device)
        # ask for threading support when sensor-functions are added

    def _device(self, device):
        self.own_dt = Config(output='class', table='object', setting=device).get()
        # if device => self.sensor doesn't need to check if enabled since it was already checked when accepting the timer
        connection = Config(setting='connection', belonging=device).get()
        if connection == 'direct':
            output = self._work(device=device, device_mapping_dict={device: Config(setting='port', belonging=device).get()})
            debugger("snake - device |direct |output '%s'" % output)
            self._write_data(device, output)
        elif connection == 'downlink': self._downlink(device, Config(setting='downlink', belonging=device).get())
        else:
            debugger("snake - device |%s has no connection configured" % device)
            Log("Device %s has no acceptable connection configured" % device, level=1).write()
            return False

    def _downlink(self, device, downlink):
        if Config(setting='enabled', belonging=downlink).get() != '1': return False
        devicetype = Config(output='class', table='object', setting=downlink).get()
        if Config(setting='enabled', belonging=devicetype).get() != '1': return False
        type_opp = Config(setting='output_per_port', belonging=devicetype).get()

        def _get_setting_dict():
            type_setting, device_setting = Config(output="setting,data", belonging=devicetype).get(), \
                                    Config(output="setting,data", belonging=downlink).get()
            setting_dict, type_setting_dict = {}, {}
            for setting, data in type_setting:
                if setting not in setting_dict.keys(): setting_dict[setting] = data
            for setting, data in device_setting: setting_dict[setting] = data
            debugger("snake - downlink |get_setting_dict |output '%s'" % setting_dict)
            return setting_dict

        if type_opp == '1':
            sensor_dict = {device: Config(setting='port', belonging=device).get()}
            debugger("snake - downlink |opp 1 |input '%s'" % sensor_dict)
            output = self._work(downlink, device_mapping_dict=sensor_dict, setting_dict=_get_setting_dict())
            debugger("snake - downlink |opp 1 |output '%s'" % output)
            self._write_data(device, output)
        elif type_opp == '0':
            portcount = Config(setting='portcount', belonging=downlink).get()
            if self.sensor_type:
                sensor_list, sensor_dict = Config(output='name', setting='downlink', filter="data = '%s'" % downlink).get(), {}
                for sensor in sensor_list:
                    if Config(output='class', table='object', setting=sensor).get() == self.sensor:
                        if sensor in self.processed_list or Config(setting='enabled', belonging=sensor).get() != '1': continue
                        sensor_dict[sensor] = Config(setting='port', belonging=sensor).get()
            else:
                sensor_dict = {device: Config(setting='port', belonging=device).get()}
            if len(sensor_dict.keys()) < portcount:
                for i in range(1, portcount):
                    if i not in sensor_dict.values():
                        sensor_dict["dummy_%s" % i] = i
                sensor_dict = {key: value for key, value in sorted(sensor_dict.items(), key=lambda item: item[1])}
            debugger("snake - downlink |opp 0 |input '%s'" % sensor_dict)
            output_dict = eval(self._work(downlink, device_mapping_dict=sensor_dict, setting_dict=_get_setting_dict()))
            debugger("snake - downlink |opp 0 |output '%s'" % output_dict)
            for sensor, data in output_dict.items():
                if sensor in self.processed_list: self._write_data(sensor, data)
        else: return False

    def _work(self, device, device_mapping_dict, setting_dict=None):
        for device in device_mapping_dict.keys():
            if device.find('dummy') == -1:
                self.processed_list.append(device)
        self._lock(device)
        function = Config(setting='function', belonging=self.own_dt).get()
        custom_arg = Config(setting='function_arg', belonging=self.own_dt, empty=True).get()
        if not custom_arg: custom_arg = None
        devicetype_class = Config(output='class', table='object', setting=self.own_dt).get()

        function_path = "%s/%s/%s" % (Config(setting='path_root').get(), devicetype_class, function)
        output = self._get_data(device=device, func_arg1=function_path, func_arg2=device_mapping_dict,
                                func_arg3=setting_dict, func_arg4=custom_arg)
        self._unlock(device)
        return output

    def _get_data(self, device, func_arg1, func_arg2, func_arg3, func_arg4):
        Log("Starting function %s for device %s.\nInput data:\nDevice mapping '%s'\nSettings '%s'\nCustom argument '%s'"
            % (func_arg1, device, func_arg2, func_arg3, func_arg4), level=4).write()
        # need to lookup python bin path dynamically
        debugger("snake - start |/usr/bin/python3.8 %s %s %s %s" % (func_arg1, func_arg2, func_arg3, func_arg4))
        output, error = process("/usr/bin/python3.8 %s \"%s\" \"%s\" \"%s\"" % (func_arg1, func_arg2, func_arg3, func_arg4),
                                out_error=True)
        Log("Function '%s' was processed for device %s.\nOutput '%s'" % (func_arg1, device, output), level=3).write()
        debugger("snake - start |output by processing '%s' '%s'" % (device, output))
        if error != '':
            Log("Error by executing %s:\n'%s'" % (device, error), level=1).write()
            debugger("snake - start |'%s' error by executing: '%s'" % (device, error))
        if output == '' or output is None or output.find('debug') != -1 or output == 'error' or output == '{}':
            debugger("snake - start |'%s' error - output is not acceptable: '%s'" % (device, output))
            Log("Error - output for device %s is empty or error.\nOutput: '%s'" % (device, output), level=2)
        return output

    def _lock(self, device):
        try_count, wait_time, max_try_count, start_time = 1, 10, 30, time_counter()
        # note: set config for wait time and timeout in db belonging to sensor_master
        while True:
            lock = VarHandler(name="lock_%s" % device).get()
            if bool(lock) is False: break
            elif int(lock) == 1:
                if try_count > max_try_count + 1:
                    debugger("snake - lock |device %s reached max retries -> giving up to get lock" % device)
                    Log("Unable to get lock for device '%s' in time. Timeout (%s sec) reached." %
                        (device, wait_time * try_count), level=1).write()
                    return False
                time_sleep(wait_time)
                if try_count % 3 == 0 or try_count % (max_try_count / 2) == 0:
                    debugger("snake - lock |device %s waiting for lock for %.2f seconds" % (device, (time_counter() - start_time)))
            else: break
            try_count += 1
        try_count -= 1
        VarHandler(name="lock_%s" % device, data=1).set()
        self.lock_list.append(device)
        debugger("snake - lock |device %s locked" % device)
        Log("Locked device '%s' (waited for %.2f sec)." % (device, (time_counter() - start_time)), level=2).write()
        return True

    def _unlock(self, device):
        VarHandler(name="lock_%s" % device).clean()
        self.lock_list.remove(device)
        debugger("snake - unlock |device %s unlocked" % device)
        Log("Unlocked device '%s'." % device, level=2).write()
        return True

    def _write_data(self, device, data):
        error_string_list = ['', 'error', '{}', 'None']
        if data is None or data in error_string_list:
            Log("Output data is empty")
            return False
        else:
            sql = DoSql("INSERT INTO ga.Data (agent,data,device) VALUES ('%s','%s','%s');" %
                        (Config('hostname').get(), data, device), write=True).start()
            Log("Wrote data for device '%s' to database. Output: '%s'" % (device, sql), level=4).write()
            return sql


if __name__ == '__main__':
    try:
        sensor = sys_argv[1]
    except (IndexError, NameError):
        raise SystemExit('No sensor provided')
    Balrog(sensor).start()
