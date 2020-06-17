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
    from core.handlers.smallconfig import Config
    from core.handlers.debug import debugger
except (ImportError, ModuleNotFoundError):
    from smallconfig import Config
    from debug import debugger

from datetime import datetime
from random import choice as random_choice


def now(time_format):
    return datetime.now().strftime(time_format)


date_year, date_month, date_year_month_day = now("%Y"), now("%m"), now("%Y-%m-%d")
time_hour_minute = now("%H-%M")
timestamp = "%Y-%m-%d %H:%M:%S"


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
        if typ in ['str', 'int'] and type(data) == list:
            if type(data) == list:
                if len(data) > 0:
                    data = data[0]
                else: return False
        if typ == 'tuple':
            if type(data) != str:
                output = tuple(data)
            else: output = tuple(data[2:-2].split("', '"))
        elif typ == 'list' and type(data) != list: output = [data]
        elif typ == 'str': output = str(data)
        elif typ == 'int': output = int(data)
        elif typ == 'float': output = float(data)
        elif typ == 'dict': output = dict(data)
        else: output = data
    except ValueError: output = data
    return output
