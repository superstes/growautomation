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
#     E-Mail: rene.rath@growautomation.at
#     Web: https://git.growautomation.at

# ga_version 0.4

from smallconfig import Config

from os import system as os_system
from os import path as os_path
from datetime import datetime
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from multiprocessing.shared_memory import ShareableList
from functools import lru_cache


def now(time_format):
    return datetime.now().strftime(time_format)


date02, date03 = now("%Y"), now("%m")


# Logs
class LogWrite(object):
    def __init__(self, output, scripttype="core", level=1):
        self.scripttype, self.output, self.log_level, self.log_path = scripttype.lower(), output, level, "../log/"

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


class VarHandler:
    def __init__(self, name=None, data=None):
        self.name, self.action, self.data, self.outtyp = name, None, data, None

    def get(self, outtyp):
        self.outtyp, self.action = outtyp, "get"
        return self._tracker()

    def set(self):
        self.action = "set"
        return self._tracker()

    def stop(self):
        self.action = "stop"
        return self._tracker()

    def clean(self):
        self.action = "clean"
        return self._tracker()

    def _tracker(self):
        updated_list = []
        try:
            action_list = self._memory(name="ga_share_action", action="get")
        except FileNotFoundError:
            try:
                action_list = self._memory(name="ga_share_action", action="set", data=[None] * 100)
            except FileExistsError:
                LogWrite("Memory block %s could not be created or opened")
                return False
        action_count = len(action_list)
        if self.action == "set":
            added, count = False, 1
            for action in action_list:
                if not None: updated_list.append(action)
                elif not added:
                    updated_list.append(self.name)
                    added = True
                else:
                    if count >= (action_count - 1): continue
                    updated_list.append(None)
                count += 1
        elif self.action == "cleanup":
            count = 1
            for action in action_list:
                if action is None:
                    updated_list.append(None)
                elif action == self.name:
                    updated_list.append(None)
                else:
                    if count >= (action_count - 1): continue
                    updated_list.append(action)
                count += 1
        elif self.action == "stop":
            for action in action_list:
                self._memory(name=action, action="clean")
        self._memory(name="ga_share_action", action="set", data=updated_list)
        self._memory()

    def _memory(self, action=None, name=None, data=None):
        if action is None: action = self.action
        if name is None: name = self.name
        if data is None: data = self.data
        if action == "set":
            memory_list = []
            if type(data) == dict:
                for key, value in data.items():
                    memory_list.append("key_'%s'" % key)
                    memory_list.append("val_'%s'" % value)
            elif type(data) == list:
                memory_list.append(data)
            else: memory_list = [data]
            memory = ShareableList(memory_list, name="ga_%s" % name)
            memory.shm.close()
        elif action == "get":
            try:
                memory = ShareableList(name="ga_%s" % name)
                if self.outtyp == "dict":
                    return_data, last_key = {}, ""
                    for _ in memory:
                        if _.find("key_'") != -1:
                            last_key = _.replace("key_'", "")[:-1]
                            return_data[last_key] = 0
                        elif _.find("val_'") != -1:
                            return_data[last_key] = _.replace("val_'", "")[:-1]
                        else: continue
                elif self.outtyp == "list": return_data = list(memory)
                elif self.outtyp == "int": return_data = int(memory)
                else: return_data = str(memory)
                memory.shm.close()
                return return_data
            except FileNotFoundError: return False
        elif action == "clean":
            memory = ShareableList(name="ga_%s" % name)
            memory.shm.close()
            memory.shm.unlink()
        else: return False


def debugger(command, hard_debug=False):
    if hard_debug: debug = True
    else: debug = True if VarHandler(name="debug").get() == "1" else False
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
