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

try:
    from core.handlers.smallconfig import Config
except (ImportError, ModuleNotFoundError):
    from smallconfig import Config

from datetime import datetime
from os import system as os_system
from os import path as os_path


def now(time_format):
    return datetime.now().strftime(time_format)


date_year, date_month = now("%Y"), now("%m")


def debugger(command, hard_debug=False, hard_only=False, level=1):
    if level > 1: return False
    if hard_debug: debug = True
    elif not hard_only:
        try:
            from core.handlers.var import VarHandler
        except (ImportError, ModuleNotFoundError):
            from varhandler import VarHandler
        debug = True if VarHandler(name='debug').get() == '1' else False
    else: debug = False
    if debug is True:
        prefix = "%s debug:" % now("%H:%M:%S")
        if type(command) == str:
            print(prefix, command)
        elif type(command) == list:
            [print(prefix, call) for call in command]
        return True
    else: return False


class Log:
    def __init__(self, output, typ='core', level=1):
        from inspect import stack as inspect_stack
        from inspect import getfile as inspect_getfile
        self.typ, self.output, self.log_level = typ.lower(), output, level
        self.name = inspect_getfile((inspect_stack()[1])[0])
        self.log_dir = "%s/%s/%s" % (Config('path_log').get(), self.typ, date_year)
        self.log_file = "%s/%s_%s.log" % (self.log_dir, date_month, self.typ)

    def _censor(self):
        return False
        # censor passwords -> check for strings in output ('IDENTIFIED by', 'pwd', 'password')

    def write(self):
        if self.typ == 'core':
            try:
                if self.log_level > Config('log_level').get('int'): return False
            except AttributeError: pass
        else:
            if self.log_level > Config('log_level').get('int'): return False
        if os_path.exists(self.log_dir) is False: os_system("mkdir -p %s" % self.log_dir)
        with open("%s/%s_%s.log" % (self.log_dir, date_month, self.typ), 'a') as logfile:
            logfile.write("%s - %s - %s\n" % (datetime.now().strftime("%H:%M:%S:%f"), self.name, self.output))
        return True

    def file(self):
        if os_path.exists(self.log_dir) is False: os_system("mkdir -p %s" % self.log_dir)
        if os_path.exists(self.log_file) is False: os_system("touch %s" % self.log_file)
        return self.log_file
