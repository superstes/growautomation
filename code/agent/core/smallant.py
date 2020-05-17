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
        self.name, self.action, self.data = name, None, data
        if name == "debug":
            self.debug = False
        else:
            self.debug = True

    def get(self, outtyp=None):
        self.action = "get"
        data = self._tracker()
        if type(data) == str:
            if outtyp == "int": return int(data)
            else: return str(data)
        elif type(data) == list and len(data) == 1:
            return str(data[0])
        return data

    def set(self):
        self.action, max_count, min_count = "set", 12, 4
        if len(str(self.name)) < 4:
            LogWrite("Name too short for memory block (min. %s characters)" % min_count)
            return False
        elif len(str(self.name)) > max_count:
            LogWrite("Name too long for memory block (max. %s characters)" % max_count)
            return False
        return self._tracker()

    def stop(self):
        self.action = "stop"
        return self._tracker()

    def clean(self):
        self.action = "clean"
        return self._tracker()

    def _tracker(self):
        if self.action != "get":
            action_list, updated_list = self._memory(name="share_action", action="get"), []
            if action_list is False and self.action == "set":
                action_list = self._memory(name="share_action", action="set", data=[None] * 100)
                if action_list is False: return False
                else: action_list = self._memory(name="share_action", action="get")
            action_count = len(list(action_list))
            if self.action == "set":
                added, count = False, 1
                for action in action_list:
                    if action is not None: updated_list.append(action)
                    elif not added:
                        updated_list.append(self.name)
                        added = True
                    else:
                        if count >= (action_count - 1): continue
                        updated_list.append(action)
                    count += 1
            elif self.action == "clean":
                count, custom_count = 1, 0
                for action in action_list:
                    if action == self.name:
                        updated_list.append(None)
                    elif action is None:
                        updated_list.append(None)
                    else:
                        updated_list.append(action)
                        custom_count += 1
                    count += 1
            elif self.action == "stop":
                for action in action_list:
                    if action is not None:
                        self._memory(name=action, action="clean")
                self._memory(name="share_action", action="clean")
                return True
            if self.action == "clean" and custom_count == 0:
                self._memory(name="share_action", action="clean")
            else: self._memory(name="share_action", action="set", data=updated_list)
        return self._memory()

    def _memory(self, action=None, name=None, data=None):
        if action is None: action = self.action
        if name is None: name = self.name
        if data is None: data = self.data
        if name is None or data == "": return False
        if action == "set" and (data is None or data == ""): return False
        if self.debug:
            debugger("smallant - varhandler - memory |input: '%s' '%s' '%s' '%s'" % (action, name, type(data), data))
        if action == "set":
            data_list = []
            if type(data) == dict:
                for key, value in data.items():
                    data_list.append("key_'%s'" % key)
                    data_list.append("val_'%s'" % value)
            elif type(data) == list:
                data_list.extend(data)
            else: data_list = [data]
            count = 1
            for _ in data_list:
                if type(_) == list:
                    if self.debug:
                        debugger("smallant - varhandler - memory |set: '%s' has bad input type - nr %s." % (type(_), count))
                    LogWrite("Invalid data-type '%s' as memory input for item nr %s." % (type(_), count))
                    return False
                count += 1
            try:
                memory = ShareableList(data_list, name="ga_%s" % name)
                if self.debug:
                    debugger("smallant - varhandler - memory |set: '%s' successful" % name)
                memory.shm.close()
            except (FileExistsError, KeyError):
                try:
                    memory = ShareableList(name="ga_%s" % name)
                    if len(memory) >= len(data_list):
                        for _ in range(len(memory)):
                            try:
                                memory[_] = data_list[_]
                            except IndexError:
                                memory[_] = None
                        if self.debug:
                            debugger("smallant - varhandler - memory |set: '%s' update successful" % name)
                        memory.shm.close()
                    else:
                        if self.debug:
                            debugger("smallant - varhandler - memory |set: cant update '%s' - too long" % name)
                        LogWrite("Memory block '%s' could not be updated.\nNew data list is too long. Old: %s, new: %s" % (name, len(memory), len(data_list)))
                        memory.shm.close()
                        return False
                except IndexError as error:
                    if self.debug:
                        debugger("smallant - varhandler - memory |set: cant update '%s' - list handling error" % name)
                    LogWrite("Memory block '%s' already exists and cannot be updated.\nError: %s" % (name, error))
                return False
        elif action == "get":
            try:
                memory = ShareableList(name="ga_%s" % name)
                data = [_ for _ in memory]
                memory.shm.close()
                if self.debug:
                    debugger("smallant - varhandler - memory |get: '%s' output '%s' '%s'" % (name, type(data), data))
                return data
            except FileNotFoundError:
                if self.debug:
                    debugger("smallant - varhandler - memory |get: '%s' not found" % name)
                LogWrite("Memory block '%s' was not found" % name)
                return False
        elif action == "clean":
            try:
                memory = ShareableList(name="ga_%s" % name)
                memory.shm.close()
                memory.shm.unlink()
                if self.debug:
                    debugger("smallant - varhandler - memory |clean: '%s' successful" % name)
            except FileNotFoundError:
                if self.debug:
                    debugger("smallant - varhandler - memory |clean: '%s' not found" % name)
                return False
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


def process(command, out_error=False, debug=False):
    if debug: debugger(command="smallant - process |input: '%s'" % command, hard_debug=True)
    output, error = subprocess_popen([command], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
    if debug: debugger(command="smallant - process |output: '%s' |error: '%s'" % (output.decode("utf-8"), error.decode("utf-8")), hard_debug=True)
    if out_error is False: return output.decode("utf-8")
    else: return output.decode("utf-8"), error.decode("utf-8")
