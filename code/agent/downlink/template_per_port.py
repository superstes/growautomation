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

# ga_version 0.5
#
# template for downlink if it should output data on per-port basis
#
# input from sensor-master
#   p.e. 'template.py "{device: port}" "{setting1: data1, setting2: data2}" "custom argument"'
# output to sensor-master -> if used for sensors
#   p.e. '22,2' (single string via print())
#
# if a soft error occurred you can exit your script/function like this:
# raise SystemExit('error')

from core.handlers.debug import Log

from sys import argv as sys_argv


def LogWrite(output: str, level=3):
    Log(output, typ='sensor', level=level).write()


try:
    device_mapping_dict = eval(sys_argv[1])
    setting_dict = eval(sys_argv[2])
    argument = sys_argv[3]
    if len(device_mapping_dict.keys()) > 1:
        LogWrite("System argument error: 'provided more than one device/port to process'", level=2)
        raise SystemExit('error')
    else:
        device, port = (device, port for device, port in device_mapping_dict.items())
except IndexError as error:
    LogWrite("System argument error: '%s'" % error, level=2)
    raise SystemExit('error')


class Device:
    def __init__(self):
        LogWrite("Processing device '%s'" % argument, level=3)

    def start(self):
        # if used for sensors:
        #   data = self._get_data()
        #   print(data)
        #   LogWrite("Data for device '%s' was delivered: '%s'." % (argument, data), level=4)
        # if used for actions
        #   self._start_action()
        raise SystemExit

    def _start_action(self):
        # if the downlink is used for actions
        # put some way to execute the action here
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
        return ''

    def _get_data(self):
        # if used for sensors
        # put some way to receive the sensor data here
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
        # you need to return the data from this function like this:
        # return YOUR_DATA_VARIABLE_HERE
        return ''


Device().start()
