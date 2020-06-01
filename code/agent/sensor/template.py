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
# template for a sensor
#
# input from sensor-master
# p.e. 'template.py "{device: port}" None "custom argument"'
#
# output to sensor-master
# p.e. '22,2' (single string via print())
#
# if a soft error occurred you can exit your script/function like this:
# raise SystemExit('error')

from core.smallant import Log

from sys import argv as sys_argv


def LogWrite(output: str, level=3):
    Log(output, typ='sensor', level=level).write()


try:
    device, port = (device, port for device, port in eval(sys_argv[1]).items())
    argument = sys_argv[3]
except IndexError as error:
    LogWrite("System argument error: %s" % error, level=2)
    raise SystemExit('error')


class Device:
    def __init__(self):
        LogWrite("Processing device '%s'" % device)

    def start(self):
        data = self._get_data()
        print(data)
        LogWrite("Data for device '%s' was delivered: '%s'." % (device, data), level=4)
        raise SystemExit

    def _get_data(self):
        # put some way to receive the sensor data here
        #
        # usable variables:
        # device -> name of the device to process
        # port -> gpio port configured for the device
        # argument -> a custom function argument as configured as configured for the devicetype
        #
        # you can log errors to the growautomation-sensor-log link this:
        # LogWrite('YOUR_ERROR_TEXT_HERE')
        # on default -> the logs will only be written to its file if the growautomation log_level is set to '3' (to not spam the logfile)
        # you can pass the loglevel on which to write the specific log via the 'level' argument - p.e.:
        # LogWrite('YOUR_ERROR_TEXT_HERE', level=2)
        #
        # you need to return the data from this function like this:
        # return YOUR_DATA_VARIABLE_HERE
        return ''


Device().start()
