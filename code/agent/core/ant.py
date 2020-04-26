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

from ga.core.config import Config
from ga.core.smallant import LogWrite as SmallLogWrite
from ga.core.smallant import debugger

from datetime import datetime
from datetime import timedelta
from os import popen as os_popen
from os import system as os_system
from os import path as os_path
from string import ascii_letters as string_ascii_letters
from string import digits as string_digits
from random import choice as random_choice
from colorama import Fore as colorama_fore
from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe
from getpass import getpass
# from functools import lru_cache

SmallLogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), level=2)


# Just vars
log_redirect = " 2>&1 | tee -a %s" % Config("path_log").get()

# Time formats


def now(time_format):
    return datetime.now().strftime(time_format)


time01, time02, time03 = now("%H-%M-%S"), now("%H:%M:%S"), now("%H-%M")
date01, date02, date03, date04 = now("%Y-%m-%d"), now("%Y"), now("%m"), now("%d")
timestamp = "%Y-%m-%d %H:%M:%S"


class ShellInput:
    def __init__(self, prompt, default="", poss="", intype="", style="", posstype="", max_value=20, min_value=2, neg=False, lower=True):
        self.prompt, self.default, self.poss, self.intype, self.style = prompt, default, poss, intype, style
        self.posstype, self.max_value, self.min_value, self.neg,  = posstype, max_value, min_value, neg
        self.style_type, self.output = ShellOutput(style=style).colors(), ""
        self.lower, self.default_str, self.poss_str = "", "", ""

    def string_check(self, to_check: str):
        to_check = str(to_check)
        char_blacklist = "!$§?^´`µ{}()><|\\*ÄÖÜüöä@,"
        if len(to_check) > self.max_value or len(to_check) < self.min_value:
            ShellOutput("Input error. Input must be between %s and %s characters long" % (self.min_value, self.max_value), style="warn", font="text")
            return False
        elif any((char in char_blacklist) for char in to_check):
            ShellOutput("Input error. Input must not include the following characters: %s" % char_blacklist, style="warn", font="text")
            return False
        else:
            return True

    def poss_check(self):
        while_count = 0

        def poss_error():
            if self.neg: ShellOutput("Input error. The following cannot be chosen: %s\n" % self.poss, style="warn", font="text")
            else: ShellOutput("Input error. Choose one of the following: %s\n" % self.poss, style="warn", font="text")
        while True:
            try:
                if while_count > 0: poss_error()
                user_input = str(input(self.style_type + "\n%s%s%s%s%s\n > " %
                                       (self.prompt, self.poss_str, self.poss, self.default_str, self.default) +
                                       colorama_fore.RESET) or self.default)
                if self.posstype != "":
                    if self.posstype == "int": user_input = int(user_input)
                    elif self.posstype == "str": user_input = str(user_input)
                if type(self.poss) == list:
                    if user_input in self.poss: input_ok = True
                    else: input_ok = False
                else:
                    if user_input == self.poss: input_ok = True
                    else: input_ok = False
                if self.neg: input_ok = not input_ok
                if input_ok: break
            except (KeyError, ValueError): poss_error()
            while_count += 1
        return user_input

    def get(self):
        if self.poss != "" or type(self.default) == bool:
            if self.neg: self.poss_str = "\nNo Poss: "
            else: self.poss_str = "\nPoss: "
        if self.default != "": self.default_str = "\nDefault: "

        whilecount = 0
        if type(self.default) == bool:
            while True:
                try:
                    self.output = {"true": True, "false": False, "yes": True, "no": False, "y": True,
                                   "n": False, "f": False, "t": True, "": self.default}[
                        input(self.style_type + "\n%s%syes/no/true/false%s%s\n > " %
                              (self.prompt, self.poss_str, self.default_str, self.default) + colorama_fore.RESET)]
                    break
                except KeyError:
                    ShellOutput("WARNING: Invalid input please enter either yes/true/no/false!\n", style="warn", font="text")
            self.lower = False
        elif type(self.default) == str:
            if self.intype == "pass" and self.default != "":
                getpass(prompt="\n%s\nRandom: %s\n > " % (self.prompt, self.default)) or "%s" % self.default
            elif self.intype == "pass":
                getpass(prompt="\n%s\n > " % self.prompt)
            elif self.intype == "passgen":
                user_input = 0
                while user_input < 8 or user_input > 99:
                    if (user_input < 8 or user_input > 99) and whilecount > 0:
                        ShellOutput("Input error. Value should be between 8 and 99.\n", style="warn", font="text")
                    whilecount += 1
                    user_input = int(input("\n%s%s%s%s%s\n > " % (self.prompt, self.poss_str, self.poss, self.default_str,
                                                                  self.default)) or "%s" % self.default)
                self.output = user_input
            elif self.intype == "free" and self.poss == "":
                while True:
                    user_input = input(self.style_type + "\n%s%s%s\n > " % (self.prompt, self.default_str, self.default) +
                                       colorama_fore.RESET) or self.default
                    if self.string_check(user_input):
                        self.output = user_input
                        break
            elif self.poss != "": self.output = self.poss_check()
            else: self.output = input(self.style_type + "\n%s%s%s\n > " % (self.prompt, self.default_str, self.default) +
                                      colorama_fore.RESET) or "%s" % self.default
        elif type(self.default) == int:
            user_input, min_value, max_value = 0, 1, 2592000
            while user_input < int(min_value) or user_input > int(max_value):
                if (user_input < int(min_value) or user_input > int(max_value)) and whilecount > 0:
                    ShellOutput("Input error. Value should be between %s and %s." % (min_value, max_value), style="warn", font="text")
                else: break
                whilecount += 1
                try: user_input = int(input("\n%s%s%s\n > " % (self.prompt, self.default_str, self.default)) or "%s" % self.default)
                except ValueError: user_input = 0
            self.output, self.lower = user_input, False
        else: raise KeyError("Default value was neither str/int/bool | Value: '%s', '%s'" % (type(self.default), self.default))

        if self.lower is False: return self.output
        else: return self.output.lower()


# Shell output
class ShellOutput(object):
    def __init__(self, output=None, font="text", style="", symbol="#"):
        self.output = output
        self.font = font
        self.style = style
        self.symbol = symbol
        self.start()

    def start(self):
        self.header() if self.font == "head" else self.line if self.font == "line" \
            else self.text() if self.output is not None else None

    def header(self):
        print("\n")
        self.line()
        print("%s" % self.output)
        self.line()
        print("\n")

    def colors(self):
        return colorama_fore.YELLOW if self.style == "warn" else colorama_fore.CYAN if self.style == "info" \
            else colorama_fore.RED if self.style == "err" \
            else colorama_fore.GREEN if self.style == "succ" else ""

    def text(self):
        print(self.colors() + "%s\n" % self.output + colorama_fore.RESET)

    def line(self):
        shellhight, shellwidth = os_popen('stty size', 'r').read().split()
        print(self.symbol * (int(shellwidth) - 1))


# Logs
class LogWrite(object):
    def __init__(self, output, typ="core", level=1):
        self.typ = typ.lower()
        self.output = output
        self.log_level = level

    def __repr__(self):
        return False if self.log_level > Config("log_level").get() else self.write()

    def file(self):
        logdir = "%s/%s/%s" % (Config("path_log").get(), self.typ, date02)
        if os_path.exists(logdir) is False: os_system("mkdir -p " + logdir)
        logfile = "%s/%s_%s.log" % (logdir, date03, self.typ)
        if os_path.exists(logfile) is False: os_system("touch %s" % logfile)
        return logfile

    def write(self):
        with open(self.file(), 'a') as logfile:
            logfile.write(datetime.now().strftime("%H:%M:%S:%f") + " ")
            logfile.write("\n%s\n" % self.output)


# File operations
class Line(object):
    def __init__(self, action, search, replace="", backup=False, file="./core.conf"):
        self.file = file
        self.backupfile = "%s_%s_%s.bak" % (file, date01, time03)
        self.backupdir = "%s/%s" % (Config("path_backup").get(), date02)
        self.action = action
        self.searchfor = search
        self.replacewith = replace
        self.backup = backup

    def __repr__(self):
        self.find() if self.action == "find" else self.delete() if self.action == "delete" else self.replace() if self.action == "replace" else self.add() if self.action == "add" else None

    def find(self):
        tmpfile = open(self.file, 'r')
        for xline in tmpfile.readlines(): return xline if xline.find(self.searchfor) != -1 else False

    def delete(self):
        os_system("sed -i%s '/%s/d' %s && mv %s %s %s" % (self.backupfile, self.searchfor, self.file, self.file, self.backupfile, self.backupdir)) if self.backup == "yes" \
            else os_system("sed -i '/%s/d' %s" % (self.searchfor, self.file))

    def replace(self):
        os_system("sed -i%s 's/%s/%s/p' %s && mv %s %s %s" % (self.backupfile, self.searchfor, self.replacewith, self.file, self.file, self.backupfile, self.backupdir)) if self.backup == "yes" \
            else os_system("sed -i 's/%s/%s/p' %s" % (self.searchfor, self.replacewith, self.file))

    def add(self):
        # insert after linenr / search = linenr
        os_system("sed -i%s '%s a %s' %s && mv %s %s %s" % (self.backupfile, self.searchfor, self.replacewith, self.file, self.file, self.backupfile, self.backupdir)) if self.backup == "yes" \
            else os_system("sed -i '%s a %s' %s" % (self.searchfor, self.replacewith, self.file))


def ga_setup_pwd_gen(stringlength):
    return ''.join(random_choice(string_ascii_letters + string_digits + "!#-_") for i in range(stringlength))


# Searches nested keys for values -> gives back the name of the nested keys
def dict_nested_search(dictionary, tosearch):
    return [(subkey if tosearch in subkey else None) for key in dictionary for subkey in dictionary[key]]


def string_check(string, maxlength=10, minlength=2):
    return False if type(string) != "str" else False if len(string) > maxlength or len(string) < minlength else False if any((char in "!%$§?^´`µ{}()°><|\\*ÄÖÜüöä@,") for char in string) else True


def dict_keycheck(dictionary, dictkey):
    return False if dictionary[dictkey] is None else True if dictkey in dictionary else False


def time_subtract(subtract, timeformat=timestamp, both=False):
    calculated = (datetime.now() - timedelta(seconds=subtract)).strftime(timeformat)
    return datetime.now().strftime(timeformat), calculated if both is True else calculated
