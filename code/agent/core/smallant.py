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

# ga_version 0.4

from .smallconfig import Config

from os import system as os_system
from os import path as os_path
from datetime import datetime
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from multiprocessing.managers import SharedMemoryManager
from multiprocessing.shared_memory import ShareableList
from functools import lru_cache


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


def share(name=None, action="get", data="", outtyp=None):
    manager = SharedMemoryManager()
    if action == "init":
        manager.start()
    elif action == "set":
        memory_list = []
        if type(data) == dict:
            for key, value in data.items():
                memory_list.append("key_'%s'" % key)
                memory_list.append("val_'%s'" % value)
        else: memory_list.append(data)
        ShareableList(memory_list, name="ga_%s" % name)
    elif action == "get":
        memory_list = ShareableList(name="ga_%s" % name)
        if outtyp == "dict":
            return_data, last_key = {}, ""
            for x in memory_list:
                if x.find("key_'") != -1:
                    last_key = x.replace("key_'", "")[:-1]
                    return_data[last_key] = 0
                elif x.find("val_'") != -1:
                    return_data[last_key] = x.replace("val_'", "")[:-1]
                else: continue
        elif outtyp == "list": return_data = list(memory_list)
        elif outtyp == "int": return_data = int(memory_list)
        else: return_data = str(memory_list)
        return return_data
    elif action == "cleanup":
        manager.shutdown()
    else: return False


def debugger(command, hard_debug=False):
    if hard_debug: debug = True
    else: debug = True if share(name="debug") == "1" else False
    if debug is True:
        if type(command) == str:
            print("debug:", command)
        elif type(command) == list:
            [print("debug:", call) for call in command]
    else: return False


@lru_cache()
def process(command, out_error=False):
    output, error = subprocess_popen([command], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
    if out_error is False: return output.decode("ascii")
    else: return output.decode("ascii"), error.decode("ascii")
