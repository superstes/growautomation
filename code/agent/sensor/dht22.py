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
# sensor function for adafruit dht22

from core.smallant import Log

from sys import argv as sys_argv
from time import sleep as time_sleep

import Adafruit_DHT


def LogWrite(output: str, level=3):
    Log(output, typ='sensor', level=level).write()


try:
    port, argument = sys_argv[1], sys_argv[4]
    arg_var_1, arg_var_2 = 'humidity', 'temperature'
    arg_var_list = [arg_var_1, arg_var_2]
except IndexError as error:
    LogWrite("System argument error: %s" % error, level=2)
    raise SystemExit
try:
    device_mapping_dict = dict(sys_argv[2])
except (IndexError, ValueError): device_mapping = False
try:
    setting_dict = dict(sys_argv[3])
except (IndexError, ValueError): pass


class Device:
    def __init__(self):
        LogWrite("Processing device '%s'" % argument, level=3)
        self.data = self._get_data()
        if not device_mapping: self.output_dict = False
        else: self.output_dict = True

    def start(self):
        if self.output_dict: self._data_mapping()
        print("%.2f" % self.data)
        LogWrite("Data for device '%s' was delivered: '%s'." % (argument, self.data), level=4)
        raise SystemExit

    def _data_mapping(self):
        self.data = zip(device_mapping_dict.keys(), list(self.data))

    def _get_data(self):
        if argument not in arg_var_list:
            LogWrite("Argument (sys-arg#4) must be one of the following: '%s'" % arg_var_list, level=2)
            raise SystemExit
        loop_count, max_retries = 1, 3
        while True:
            def error_check(data, max, min):
                if data is None:
                    LogWrite("Device '%s' - output error - data is none" % argument, level=2)
                elif max > float(data) > min: return True
                else:
                    LogWrite("Device '%s' - output error - not in acceptable range - data '%s', max '%s', min '%s'"
                             % (argument, data, max, min), level=2)
                return False

            if loop_count >= max_retries:
                LogWrite("Device '%s' - repeated error - max retries reached" % argument, level=1)
                raise SystemExit('error')

            humidity, temperature = Adafruit_DHT.read_retry(sensor=Adafruit_DHT.DHT22, pin=port, retries=3, delay_seconds=2)

            if argument == arg_var_1:
                if error_check(data=humidity, max=100, min=1) is True:
                    return humidity
            elif argument == arg_var_2:
                if error_check(data=temperature, max=80, min=-15) is True:
                    return temperature

            time_sleep(3)
            loop_count += 1


Device().start()
