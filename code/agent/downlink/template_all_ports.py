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
#
# template for downlink if it should output data for all ports at once
#
# input from sensor-master
#   p.e. 'template.py "{device1: port1, device2: port2}" "{setting1: data1, setting2: data2}" "custom argument"'
# output to sensor-master
#   p.e. '{device1: data1, device2: data2}'
#
# if a soft error occurred you can exit your script/function like this:
# raise SystemExit('error')

from core.smallant import Log

from sys import argv as sys_argv


def LogWrite(output: str, level=3):
    Log(output, typ='sensor', level=level).write()


try:
    device_mapping_dict = eval(sys_argv[1])
    setting_dict = dict(sys_argv[2])
    argument = sys_argv[3]
    if len(device_mapping_dict.keys()) < 2:
        LogWrite("System argument error: 'provided less than two devices/ports to process'", level=2)
        raise SystemExit('error')
except IndexError as error:
    LogWrite("System argument error: '%s'" % error, level=2)
    raise SystemExit('error')


class Device:
    def __init__(self):
        LogWrite("Processing device '%s'" % argument, level=3)

    def start(self):
        data = self._get_data()
        print(data)
        LogWrite("Data for device '%s' was delivered: '%s'." % (argument, data), level=4)
        raise SystemExit

    def _get_data(self):
        # put some way to receive the data from its child-sensors
        #
        # data output:
        #   this downlink must return a dictionary of devices and data to the sensor-master
        #   p.e. if the downlink has 4-downlink-ports:
        #     {device1: data1, device2: data2, device3: data3, device4: data4}
        #
        # usable variables:
        #   device -> name of the device to process
        #   port -> downlink port configured for the device
        #   argument -> a custom function argument as configured as configured for the devicetype
        #   setting_dict -> all settings available for this downlink device
        #
        # you can log errors to the growautomation-sensor-log link this:
        #   LogWrite('YOUR_ERROR_TEXT_HERE')
        #   on default -> the logs will only be written to its file if the growautomation log_level is set to '3' (to not spam the logfile)
        #   you can pass the loglevel on which to write the specific log via the 'level' argument - p.e.:
        #   LogWrite('YOUR_ERROR_TEXT_HERE', level=2)
        #
        # data returning template:
        #   data_list = ['P1_DATA', 'P2_DATA', 'P3_DATA', 'P4_DATA']
        #   if len(list(data_list)) == len(device_mapping_dict.keys()):
        #       return dict(zip(device_mapping_dict.keys(), list(data_list)))
        #   else:
        #       LogWrite('Not received data for each port on the downlink.', level=2)
        #       raise SystemExit('error')
        return ''


Device().start()
