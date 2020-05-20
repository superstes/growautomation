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

from core.config import Config
from core.owl import DoSql
from core.smallant import Log
from core.smallant import debugger
from core.smallant import VarHandler
from core.smallant import process

from sys import argv as sys_argv
from time import sleep as time_sleep
from sys import exc_info as sys_exc_info
import signal


class Balrog:
    def __init__(self, sensor):
        self.sensor, self.own_dt = sensor, None
        self.processed_list, self.lock_list = [], []
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT, self._stop)
        self.sensor_type = True if self.sensor in Config(output='name', table='object', filter="class = 'sensor'").get('list') else False
        self.devicetype() if self.sensor_type is True else self.device(self.sensor)

    def devicetype(self):
        device_list, self.own_dt = [], self.sensor
        # check all for loops if they will break if only one element is in list -> find clean solution
        for device in Config(output='name', table='object', filter="class = '%s'" % self.sensor).get('list'):
            if not Config(setting='timer', belonging=device, empty=True).get() and Config(setting='enabled', belonging=device).get() == '1':
                device_list.append(device)
        for device in device_list:
            if device in self.processed_list: continue
            else: self.device(device)
        # ask for threading support when sensor-functions are added

    def device(self, device):
        self.own_dt = Config(output='class', table='object', setting=device).get()
        # if device => self.sensor doesn't need to check if enabled since it was already checked when accepting the timer
        connection = Config(setting='connection', belonging=device).get()
        if connection == 'direct':
            output = self._start(device)
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
            type_setting, setting = Config(output="setting,data", belonging=devicetype).get(), Config(output="setting,data", belonging=downlink).get()
            setting_dict, type_setting_dict = {}, {}
            for setting, data in setting: setting_dict[setting] = data
            for setting, data in type_setting:
                if setting not in setting_dict.keys(): setting_dict[setting] = data
            debugger("snake - downlink |get_setting_dict |output '%s'" % setting_dict)
            return setting_dict

        if type_opp == '1':
            sensor_dict = {device: Config(setting='port', belonging=device).get()}
            debugger("snake - downlink |opp 1 |input '%s'" % sensor_dict)
            output = self._start(downlink, device_mapping_dict=sensor_dict, setting_dict=get_setting_dict())
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
                for i in range(portcount):
                    if i not in sensor_dict.values():
                        sensor_dict["dummy_%s" % i] = i
                        # portlist in dict will start at 0 => throw it into the docs
                sensor_dict = {key: value for key, value in sorted(sensor_dict.items(), key=lambda item: item[1])}
            debugger("snake - downlink |opp 0 |input '%s'" % sensor_dict)
            output_dict = self._start(downlink, device_mapping_dict=sensor_dict, setting_dict=get_setting_dict())
            debugger("snake - downlink |opp 0 |output '%s'" % output_dict)
            for sensor, data in output_dict.items():
                if sensor in self.processed_list: self._write_data(sensor, data)
            # if opp -> output must be string
            # if not opp -> output must be dict with sensor as key and data as value
        else: return False

    def _start(self, device, device_mapping_dict=None, setting_dict=None):
        if device_mapping_dict is None: self.processed_list.extend(device)
        else:
            for device in device_mapping_dict.keys():
                if device.find('dummy') == -1: self.processed_list.append(device)
        self._lock(device)
        function = Config(setting='function', belonging=self.own_dt).get()
        custom_arg = Config(setting='function_arg', belonging=self.own_dt, empty=True).get()
        if not custom_arg: custom_arg = None
        port = Config(setting='port', belonging=device).get()
        devicetype_class = Config(output='class', table='object', setting=self.own_dt).get()

        function_path = "%s/%s/%s" % (Config(setting='path_root').get(), devicetype_class, function)
        Log("Starting function %s for device %s.\nInput data:\nDevice mapping '%s'\nSettings '%s'"
            % (function_path, device, device_mapping_dict, setting_dict), level=4).write()
        debugger("snake - start |/usr/bin/python3 %s %s %s %s %s" %
                 (function_path, port, device_mapping_dict, setting_dict, custom_arg))
        output, error = process("/usr/bin/python3 %s %s %s %s %s" %
                                (function_path, port, device_mapping_dict, setting_dict, custom_arg), out_error=True)
        Log("Function '%s' was processed for device %s.\nOutput '%s'" % (function_path, device, output), level=3).write()
        debugger("snake - start |output by processing %s '%s'" % (device, output))
        if error != '':
            Log("Error by executing %s:\n'%s'" % (device, error), level=2).write()
            debugger("snake - start |error by executing %s '%s'" % (device, error))
        if device_mapping_dict is None: return output
        else: return dict(output)

    def _lock(self, device):
        try_count, wait_time, max_try_count = 1, 10, 31
        # note: set config for wait time and timeout in db belonging to sensor_master
        while True:
            if VarHandler(name="lock_%s" % device).get('int') == 1: time_sleep(wait_time)
            else: break
            if try_count > max_try_count:
                debugger("snake - lock |device %s reached max retries -> giving up to get lock" % device)
                Log("Unable to get lock for device '%s' in time. Timeout (%s sec) reached." % (device, wait_time * try_count), level=2).write()
                return False
            debugger("snake - lock |device %s waiting for lock for % seconds" % (device, wait_time * try_count))
            try_count += 1
        try_count -= 1
        VarHandler(name="lock_%s" % device, data=1).set()
        self.lock_list.append(device)
        debugger("snake - lock |device %s locked" % device)
        Log("Locked device '%s' (waited for ~%s sec)." % (device, wait_time * try_count), level=2).write()
        return True

    def _unlock(self, device):
        VarHandler(name="lock_%s" % device, data=0).clean()
        self.lock_list.remove(device)
        debugger("snake - unlock |device %s unlocked" % device)
        Log("Unlocked device '%s'." % device, level=2).write()
        return True

    def _write_data(self, device, data):
        sql = DoSql("INSERT INTO ga.Data (agent,data,device) VALUES ('%s','%s','%s');" % (Config('hostname').get(), data, device), write=True).start()
        Log("Wrote data for device '%s' to database. Output: %s" % (device, sql), level=4).write()
        return sql

    def _stop(self, signum=None, stack=None):
        if signum is not None:
            debugger("snake - stop |got signal %s - '%s'" % (signum, sys_exc_info()[0].__name__))
            Log("Sensor master received signal %s - '%s'" % (signum, sys_exc_info()[0].__name__), level=2).write()
        if len(self.lock_list) > 0:
            unlock_list = self.lock_list
            for device in unlock_list: self._unlock(device)
            debugger("snake - stop |unlocked following devices '%s'" % unlock_list)
        debugger('snake - stop |exiting')
        raise SystemExit


try: Balrog(sys_argv[1])
except IndexError:
    Log('No sensor provided. Exiting.').write()
    raise SystemExit
