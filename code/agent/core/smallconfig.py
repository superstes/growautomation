#!/usr/bin/python3.8
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

from functools import lru_cache
from os import path as os_path
from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe


class Config:
    def __init__(self, request, file='core.conf'):
        self.file, self.request = file, request

    def get(self, out_type='str'):
        if self.file == 'core.conf':
            file = "%s/%s" % (os_path.dirname(os_path.realpath(__file__)), self.file)
            self.file = file
        output = self._parse_file()
        try:
            if out_type == 'int':
                return int(output)
            elif out_type == 'dict':
                return dict(output)
            elif out_type == 'list':
                return list(output)
            else:
                return str(output)
        except ValueError:
            return str(output)

    def _error(self, parser_type):
        from core.shared.debug import Log
        Log("Current module: '%s'" % inspect_getfile(inspect_currentframe()), level=2).write()
        Log("%s parser could not find setting '%s'" % (parser_type.capitalize(), self.request), level=1).write()
        return False

    def _parse_file_find(self):
        try:
            with open(self.file, 'r') as config_file:
                for line in config_file.readlines():
                    if line.find(self.request) != -1:
                        return line
                return False
        except FileNotFoundError: return False

    @lru_cache()
    def _parse_file(self):
        response = self._parse_file_find()
        if response is False or response is None or response == '':
            hardcode_dict = {'path_root': '/etc/growautomation', 'path_log': '/var/log/growautomation', 'log_level': '1'}
            if self.request in hardcode_dict.keys(): return hardcode_dict[self.request]
            self._error('file')
            return False
        else:
            try:
                split = response.split('=')[1].strip()
                return split
            except (IndexError, ValueError):
                self._error('file')
