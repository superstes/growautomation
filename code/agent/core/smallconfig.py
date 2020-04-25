#!/usr/bin/python
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

from functools import lru_cache
from os import path as os_path
from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe


class Config(object):
    def __init__(self, request, file="core.conf"):
        global tmp_dict
        self.file, self.request, tmp_dict = file, request, {}

    def get(self):
        if self.file == "core.conf":
            file = "%s/%s" % (os_path.dirname(os_path.realpath(__file__)), self.file)
            self.file = file
        return self.parse_file()

    def error(self, parser_type):
        from ga.core.smallant import LogWrite
        LogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), level=2)
        LogWrite("%s parser could not find setting %s" % (parser_type.capitalize(), self.request))
        raise SystemExit("%s parser could not find setting %s" % (parser_type.capitalize(), self.request))

    def parse_file_find(self):
        tmpfile = open(self.file, 'r')
        for xline in tmpfile.readlines():
            if xline.find(self.request) != -1:
                return xline
        return False

    @lru_cache()
    def parse_file(self):
        response = self.parse_file_find()
        if response is False or response is None or response == "":
            self.error("file")
        else:
            try:
                split = response.split("=")[1].strip()
                return split
            except (IndexError, ValueError):
                self.error("file")