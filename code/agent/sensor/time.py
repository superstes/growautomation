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

from core.smallant import now

from sys import argv as sys_argv

try:
    for _1, _2 in eval(sys_argv[1]).items():
        device, port = _1, _2
    argument = sys_argv[3]
    arg_var_1, arg_var_2 = 'time', 'date'
    arg_var_list = [arg_var_1, arg_var_2]
except IndexError as error:
    raise SystemExit('error')


class Device:
    def __init__(self):
        self.data = self._get_data()

    def start(self):
        print(self.data)
        raise SystemExit

    def _get_data(self):
        if argument not in arg_var_list:
            raise SystemExit('error')
        if argument == 'time':
            return now("%H-%M-%S")
        elif argument == 'date':
            return now("%Y-%m-%d")


Device().start()
