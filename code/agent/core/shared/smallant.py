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

# provides functions/classes that are used throughout the project (and don't need other core modules)

try:
    from core.smallconfig import Config
except (ImportError, ModuleNotFoundError):
    from smallconfig import Config
from varhandler import VarHandler

from os import system as os_system
from os import path as os_path
from datetime import datetime
from time import sleep as time_sleep
from random import choice as random_choice


def now(time_format):
    return datetime.now().strftime(time_format)


date_year, date_month, date_year_month_day = now("%Y"), now("%m"), now("%Y-%m-%d")
time_hour_minute = now("%H-%M")
timestamp = "%Y-%m-%d %H:%M:%S"


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
    from subprocess import Popen as subprocess_popen
    from subprocess import PIPE as subprocess_pipe
    if debug: debugger(command="smallant - process |input: '%s'" % command, hard_debug=True)
    output, error = subprocess_popen([command], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
    output, error = output.decode('utf-8').strip(), error.decode('utf-8').strip()
    if debug: debugger(command="smallant - process |output: '%s' '%s' |error: '%s' '%s'"
                               % (type(output), output, type(error), error), hard_debug=True)
    if out_error is False: return output
    else: return output, error


def internal_process(target, argument=None, stdout=True, debug=False):
    from multiprocessing import Process as MP_Process
    from multiprocessing import Queue as MP_Queue
    if debug: debugger(command="smallant - internal_process |input: '%s' '%s'" % (type(target), target.__name__), hard_debug=True)
    stdout_pipe = MP_Queue()
    if stdout is True: _process = MP_Process(target=target, args=(argument, stdout_pipe))
    else: _process = MP_Process(target=target, args=argument)
    _process.start()
    runtime_count, finished = 1, False
    while True:
        if not _process.is_alive():
            _process.join()
            if stdout is True:
                output = stdout_pipe.get()
                if debug: debugger(command="smallant - internal_process |output: '%s' '%s'" % (type(output), output), hard_debug=True)
                return output
            return True
        elif runtime_count > 5:
            _process.terminate()
            _process.join()
            if debug: debugger(command="smallant - internal_process |timeout - terminated", hard_debug=True)
            return False
        else: time_sleep(3)
        runtime_count += 1


def list_remove_duplicates(_list):
    return list(dict.fromkeys(_list))


def ga_setup_pwd_gen(stringlength):
    from string import ascii_letters as string_ascii_letters
    from string import digits as string_digits
    return ''.join(random_choice(string_ascii_letters + string_digits + '!#-_') for i in range(stringlength))


def dict_nested_search(dictionary, tosearch):
    # Searches nested keys for values -> gives back the name of the nested keys
    return [(subkey if tosearch in subkey else None) for key in dictionary for subkey in dictionary[key]]


def dict_sort_keys(list_of_dict: list):
    output_list = []
    try:
        sorted_key_list = sorted([key for _dict in list_of_dict for key in dict(_dict).keys()])
        for key in sorted_key_list:
            output_list.append({key: list_of_dict[key]})
    except TypeError: output_list = list_of_dict
    return output_list


def dict_keycheck(dictionary, dictkey):
    return False if dictionary[dictkey] is None else True if dictkey in dictionary else False


def string_check(string, maxlength=10, minlength=2):
    if type(string) != 'str': return False
    elif (len(string) > maxlength or len(string) < minlength) or (any((char in "!%$§?^´`µ{}()°><|\\*ÄÖÜüöä@,") for char in string)):
        return False
    else: return True


def time_subtract(subtract, timeformat=timestamp, both=False):
    from datetime import timedelta
    calculated = (datetime.now() - timedelta(seconds=subtract)).strftime(timeformat)
    return datetime.now().strftime(timeformat), calculated if both is True else calculated


def plural(data):
    def _base_check(nr):
        if nr > 1: return 's'
        else: return ''
    if type(data) == int: return _base_check(data)
    elif type(data) == list: return _base_check(len(data))
    elif type(data) == str:
        try:
            return _base_check(int(data))
        except ValueError:
            return ''
    else: return ''


def int_leading_zero(length: int, number: int):
    digits = len(str(number))
    if digits < length:
        return "%s%s" % ('0' * (length - digits), number)
    elif digits == length:
        return number
    else: return False


class ModifyIdiedDict:
    def __init__(self, dict_to_process: dict):
        self.dict = dict_to_process

    def add(self, id_new: int, data: dict):
        new_dict, added = {}, False
        for i in range(1, len(self.dict) + 2):
            if i == id_new:
                new_dict[i] = data
                added = True
            elif added is False:
                new_dict[i] = self.dict[i]
            else: new_dict[i] = self.dict[i - 1]
        return new_dict

    def delete(self, id_del: int):
        new_dict, deleted = {}, False
        for i in range(1, len(self.dict) + 1):
            if i == id_del:
                deleted = True
            elif deleted is False:
                new_dict[i] = self.dict[i]
            else: new_dict[i - 1] = self.dict[i]
        return new_dict

    def edit(self, id_old: int, id_new: int, data_new=None):
        new_dict, change = {}, 0
        for i in range(1, len(self.dict) + 1):
            if i == id_new:
                if data_new is not None: data = data_new
                else: data = self.dict[id_old]
                new_dict[i] = data
                change -= 1
            elif i == id_old:
                if change == 0: change += 1
                new_dict[i] = self.dict[i + change]
                if change == -1: change += 1
            else: new_dict[i] = self.dict[i + change]
        return new_dict


def format_output(typ, data):
    try:
        if typ == 'list' and type(data) != list:
            output = [data]
        elif typ == 'str' and type(data) != str:
            if type(data) == list:
                if len(data) > 0: output = data[0]
                else: output = ''
            else: output = str(data)
        elif typ == 'int':
            output = int(data)
        elif typ == 'tuple':
            if type(data) != str:
                output = tuple(data)
            else: output = tuple(data[2:-2].split("', '"))
        elif typ == 'dict':
            output = dict(data)
        else: output = data
    except ValueError: output = data
    return output
