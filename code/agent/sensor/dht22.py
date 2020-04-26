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
# sensor function for adafruit dht22

from ga.core.ant import LogWrite as LogModule
from ga.core.smallant import debugger

from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe
from sys import argv as sys_argv

import Adafruit_DHT


def LogWrite(log: str, level=3):
    LogModule(log, typ="downlink", level=level)


function = inspect_getfile(inspect_currentframe())
LogWrite("Current module: %s" % function, level=2)

try:
    argument = sys_argv[1]
    port = sys_argv[2]
except (IndexError, ValueError) as error:
    LogWrite("System argument error: %s" % error, level=2)
    debugger("%s - sys_argv error: %s" % (function, error))
    raise SystemExit
try:
    device_mapping_dict = dict(sys_argv[3])
except (IndexError, ValueError):
    device_mapping = False
    debugger("%s - sys_argv not device_mapping_dict" % function)
try:
    setting_dict = dict(sys_argv[4])
except (IndexError, ValueError):
    debugger("%s - sys_argv not setting_dict" % function)


class Device:
    def __init__(self):
        self.data = self.get_data()
        if not device_mapping: self.output_dict = False
        else: self.output_dict = True

    def start(self):
        debugger("%s - start |starting get_data |argument '%s' '%s'|port '%s' '%s'" % (type(argument), argument), type(port), port)
        if self.output_dict: self.data_mapping()
        print(self.data)
        LogWrite("Data was delivered.", level=4)
        debugger("%s - start |finished")
        raise SystemExit

    def data_mapping(self):
        self.data = zip(device_mapping_dict.keys(), list(self.data))
        debugger("%s - data_mapping |%s" % (function, self.data))

    def get_data(self):
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, port)
        if argument == "humi": return humidity
        elif argument == "temp": return temperature
        else: LogWrite("Input Error: Either define humidity or temperature")


Device().start()
