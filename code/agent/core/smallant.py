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
try:
    from core.smallconfig import Config
except (ImportError, ModuleNotFoundError):
    from smallconfig import Config

from os import system as os_system
from os import path as os_path
from os import getenv as os_getenv
from datetime import datetime
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from multiprocessing.shared_memory import ShareableList
from inspect import stack as inspect_stack
from inspect import getfile as inspect_getfile
from random import choice as random_choice


def now(time_format):
    return datetime.now().strftime(time_format)


date_year, date_month = now("%Y"), now("%m")


# Logs
class Log:
    def __init__(self, output, typ='core', level=1):
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


class VarHandler:
    def __init__(self, name=None, data=None):
        self.name, self.action, self.data = name, None, data

    def get(self, outtyp=None):
        self.action = 'get'
        data = self._tracker()
        if type(data) == str:
            if outtyp == 'int': data = int(data)
            else: data = str(data)
        elif type(data) == list and len(data) == 1:
            data = str(data[0])
        self._debug("smallant - varhandler - tracker |request '%s', output '%s' '%s'" % (self.name, type(data), data), skip_hard=True)
        return data

    def set(self):
        self.action, max_count, min_count = 'set', 12, 4
        if len(str(self.name)) < 4:
            Log("Name too short for memory block (min. %s characters)" % min_count).write()
            return False
        elif len(str(self.name)) > max_count:
            Log("Name too long for memory block (max. %s characters)" % max_count).write()
            return False
        return self._tracker()

    def stop(self):
        self.action = 'stop'
        return self._tracker()

    def clean(self):
        self.action = 'clean'
        return self._tracker()

    def _debug(self, output, skip_hard=False, log=False, level=1, name=None):
        if name is None: name = self.name
        if name == 'debug' and skip_hard and not log: return False
        elif os_getenv('USER') == 'growautomation' and not log:
            debugger(output, hard_only=True, level=1)
        elif name == 'debug' and not log:
            debugger(output, hard_debug=True, level=1)
        else:
            if log: Log(output, level=level).write()
            else: debugger(output, level=level)

    def _tracker(self):
        if self.action != 'get':
            action_list, updated_list, action_count = self._memory(name='share_action', action='get'), [], 25
            if action_list is False and self.action == 'set':
                self._memory(name='share_action', action='set', data=['dummy_entry_%s' % nr for nr in range(action_count)])
                action_list = self._memory(name='share_action', action='get')
                if action_list is False: return False
                else: action_list = self._memory(name='share_action', action='get')
            self._debug("smallant - varhandler - tracker |action_list '%s' '%s'" % (type(action_list), action_list))
            if type(action_list) == bool: return False

            def add_new_dummy(_count, _updated_list, once=False):
                while action_count > _count:
                    loop_count = 0
                    while True:
                        rand_nr, find = ''.join([random_choice('0123456789') for _ in range(4)]), False
                        for action in _updated_list:
                            if action.find(rand_nr) != -1: find = True
                        if find is False:
                            _updated_list.append('dummy_new_%s' % rand_nr)
                            _count += 1
                            break
                        if loop_count > 5:
                            _updated_list.append('dummy_new_0')
                            _count += 1
                            break
                        loop_count += 1
                    if once: break
                return _count, _updated_list

            if self.action == 'set':
                added, count = False, 1
                if self.name not in action_list:
                    for action in action_list:
                        if action.find('dummy') == -1:
                            updated_list.append(action)
                        elif not added:
                            updated_list.append(self.name)
                            added = True
                        else: updated_list.append(action)
                        count += 1
                else:
                    count = len(action_list)
                    updated_list = action_list
                count, updated_list = add_new_dummy(count, updated_list)
            elif self.action == 'clean':
                count, custom_count = 1, 0
                for action in action_list:
                    if action == self.name:
                        count, updated_list = add_new_dummy(count, updated_list, once=True)
                    else:
                        updated_list.append(action)
                        custom_count += 1
                    count += 1
            elif self.action == 'stop':
                for action in action_list:
                    if action.find('dummy') == -1:
                        self._memory(name=action, action='clean')
                self._memory(name='share_action', action='clean')
                return True

            self._debug("smallant - varhandler - tracker |updated_list '%s' '%s'" % (type(updated_list), updated_list))
            self._memory(name='share_action', action='set', data=updated_list)
            if self.action == 'clean' and custom_count == 0:
                self._memory(name='share_action', action='clean')
                return True
        return self._memory()

    def _memory(self, action=None, name=None, data=None):
        if action is None: action = self.action
        if name is None: name = self.name
        if data is None: data = self.data
        if name is None or data == '': return False
        if action == 'set' and (data is None or data == ''): return False

        self._debug("smallant - varhandler - memory |input: '%s' '%s' '%s' '%s'" %
                    (action, name, type(data), data), skip_hard=True, level=2, name=name)
        if action == 'set':
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
                    self._debug("smallant - varhandler - memory |set: '%s' has bad input type - nr %s." % (type(_), count), name=name)
                    self._debug("Invalid data-type '%s' as memory input for item nr %s." % (type(_), count), log=True, name=name)
                    return False
                count += 1
            try:
                memory = ShareableList(data_list, name="ga_%s" % name)
                self._debug("smallant - varhandler - memory |set: '%s' successful" % name, name=name)
                memory.shm.close()
                return True
            except (FileExistsError, KeyError):
                try:
                    memory = ShareableList(name="ga_%s" % name)
                    if len(data_list) > len(list(memory)):
                        self._debug("smallant - varhandler - memory |set: cant update '%s' - too long" % name, name=name)
                        self._debug("Memory block '%s' could not be updated.\nNew data list is too long. Old: %s, new: %s"
                                    % (name, len(memory), len(data_list)), log=True, name=name)
                        memory.shm.close()
                    else:
                        for _ in range(len(memory)):
                            try:
                                memory[_] = data_list[_]
                            except IndexError:
                                memory[_] = None
                        self._debug("smallant - varhandler - memory |set: '%s' update successful" % name, name=name)
                        memory.shm.close()
                except (IndexError, KeyError) as error:
                    self._debug("smallant - varhandler - memory |set: cant update '%s' - list handling error" % name, name=name)
                    self._debug("Memory block '%s' already exists and cannot be updated.\nError: %s" %
                                (name, error), log=True, level=2, name=name)
                return False
        elif action == 'get':
            try:
                memory = ShareableList(name="ga_%s" % name)
                data = [_ for _ in memory]
                memory.shm.close()
                self._debug("smallant - varhandler - memory |get: '%s' output '%s' '%s'" %
                            (name, type(data), data), skip_hard=True, level=2, name=name)
                return data
            except (FileNotFoundError, KeyError):
                self._debug("smallant - varhandler - memory |get: '%s' not found" % name, skip_hard=True, name=name)
                self._debug("Memory block '%s' was not found" % name, log=True, level=3, name=name)
                return False
        elif action == 'clean':
            try:
                memory = ShareableList(name="ga_%s" % name)
                memory.shm.close()
                memory.shm.unlink()
                self._debug("smallant - varhandler - memory |clean: '%s' successful" % name, name=name)
                return True
            except (FileNotFoundError, KeyError):
                self._debug("smallant - varhandler - memory |clean: '%s' not found" % name, name=name)
                return False
        else: return False


def debugger(command, hard_debug=False, hard_only=False, level=1):
    if level > 1: return False
    if hard_debug: debug = True
    elif not hard_only:
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


def process(command, out_error=False, debug=False):
    if debug: debugger(command="smallant - process |input: '%s'" % command, hard_debug=True)
    output, error = subprocess_popen([command], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
    if debug: debugger(command="smallant - process |output: '%s' |error: '%s'" % (output.decode('utf-8'), error.decode('utf-8')), hard_debug=True)
    if out_error is False: return output.decode('utf-8')
    else: return output.decode('utf-8').strip(), error.decode('utf-8').strip()
