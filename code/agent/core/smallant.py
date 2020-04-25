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

from ga.core.smallconfig import Config

from os import system as os_system
from os import path as os_path
from datetime import datetime


def now(time_format):
    return datetime.now().strftime(time_format)


date02, date03 = now("%Y"), now("%m")


# Logs
class LogWrite(object):
    def __init__(self, output, scripttype="core", level=1):
        self.scripttype = scripttype.lower()
        self.output = output
        self.log_level = level
        self.log_path = "../log/"

    def __repr__(self):
        try:
            return False if self.log_level > Config("log_level").get() else self.write()
        except AttributeError: self.write()

    def open(self):
        logdir = "%s/%s/%s" % (self.log_path, self.scripttype, date02)
        if os_path.exists(logdir) is False: os_system("mkdir -p " + logdir)
        return open("%s/%s_%s.log" % (logdir, date03, self.scripttype), 'a')

    def write(self):
        logfile = self.open()
        logfile.write(datetime.now().strftime("%H:%M:%S:%f") + " ")
        logfile.write("\n%s\n" % self.output)
        logfile.close()


def debugger(command, hard_debug=False):
    try:
        from ga.core.globalvars import tmp_dict
        if hard_debug: debug = True
        else:
            if tmp_dict["debug"] == 1: debug = True
            else: debug = False
        if debug is True:
            if type(command) == str:
                print("debug:", command)
            elif type(command) == list:
                [print("debug:", call) for call in command]
    except (KeyError, ImportError) as error: LogWrite(error)


def debug_init(on=True):
    from ga.core.globalvars import init_vars
    init_vars()
    from ga.core.globalvars import tmp_dict
    if on: tmp_dict["debug"] = 1
    else: tmp_dict["debug"] = 0
