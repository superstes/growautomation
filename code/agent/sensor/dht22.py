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

import Adafruit_DHT


def LogWrite(output: str, level=3):
    Log(output, typ='sensor', level=level).write()


try:
    port, argument = sys_argv[1], sys_argv[4]
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
        self.data = self._get_data()
        if not device_mapping: self.output_dict = False
        else: self.output_dict = True

    def start(self):
        if self.output_dict: self._data_mapping()
        print("%.2f" % self.data)
        LogWrite('Data was delivered.', level=4)
        raise SystemExit

    def _data_mapping(self):
        self.data = zip(device_mapping_dict.keys(), list(self.data))

    def _get_data(self):
        if argument != 'humidity' and argument != 'temperature':
            raise ValueError("Argument (sys-arg#4) must be either 'humidity' or 'temperature'!")
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, port)
        if argument == 'humidity': return humidity
        elif argument == 'temperature': return temperature
        else: Log('Input Error: Either define humidity or temperature').write()


Device().start()
