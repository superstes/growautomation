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

#ga_version0.3

from datetime import datetime
from os import popen as os_popen
from os import path as os_path
from os import system as os_system
from string import ascii_letters as string_ascii_letters
from string import digits as string_digits
from random import choice as random_choice
from colorama import Fore as colorama_fore
# from functools import lru_cache

from ga.core import config


# Just vars
log_redirect = " 2>&1 | tee -a %s" % config.do("path_log")

# Time formats

time01 = datetime.now().strftime("%H-%M-%S")
time02 = datetime.now().strftime("%H:%M:%S")
time03 = datetime.now().strftime("%H-%M")

date01 = datetime.now().strftime("%Y-%m-%d")
date02 = datetime.now().strftime("%Y")
date03 = datetime.now().strftime("%m")
date04 = datetime.now().strftime("%d")


# Shell output
class shell(object):
    def __init__(self, output, font="text", style="info", symbol="#"):
        self.output = output
        self.font = font
        self.style = style
        self.symbol = symbol
        self.start()

    def start(self):
        if self.font == "text":
            self.text()
        elif self.font == "head":
            self.header()

    def header(self):
        shellhight, shellwidth = os_popen('stty size', 'r').read().split()
        print("\n%s\n%s\n%s\n" % (self.symbol * (int(shellwidth) - 1), self.output, self.symbol * (int(shellwidth) - 1)))

    def colors(self):
        if self.style == "warn":
            return colorama_fore.YELLOW
        elif self.style == "info":
            return colorama_fore.CYAN
        elif self.style == "err":
            return colorama_fore.RED
        elif self.style == "succ":
            return colorama_fore.GREEN
        else:
            return ""

    def text(self):
        print(self.colors() + "%s\n" % self.output + colorama_fore.RESET)


# Logs
class log(object):
    def __init__(self, output, scripttype, loglevel=2):
        self.scripttype = scripttype.lower()
        self.output = output
        self.loglevel = loglevel
        self.check()

    def open(self):
        logdir = "%s/%s/%s" % (config.do("path_log"), self.scripttype, date02)
        if os_path.exists(logdir) is False:
            os_system("mkdir -p " + logdir)
        return open("%s/%s_%s.log" % (logdir, date03, self.scripttype), 'a')

    def write(self):
        logfile = self.open()
        logfile.write(datetime.now().strftime("%H:%M:%S:%f") + " ")
        logfile.write("\n%s\n" % self.output)
        logfile.close()

    def check(self):
        if self.loglevel > config.do("log_level"):
            return False
        else:
            self.write()


# File operations
class line(object):
    def __init__(self, action, search, replace="", backup=False, file="./core.conf"):
        self.file = file
        self.backupfile = "%s_%s_%s.bak" % (file, date01, time03)
        self.backupdir = "%s/%s" % (config.do("path_backup"), date02)
        self.action = action
        self.searchfor = search
        self.replacewith = replace
        self.backup = backup
        self.start()

    def start(self):
        if self.action == "find":
            self.find()
        elif self.action == "delete":
            self.delete()
        elif self.action == "replace":
            self.replace()
        elif self.action == "add":
            self.add()

    def find(self):
        tmpfile = open(self.file, 'r')
        for xline in tmpfile.readlines():
            if xline.find(self.searchfor) != -1:
                return xline
        return False

    def delete(self):
        if self.backup == "yes":
            os_system("sed -i%s '/%s/d' %s && mv %s %s %s" % (self.backupfile, self.searchfor, self.file, self.file, self.backupfile, self.backupdir))
        else:
            os_system("sed -i '/%s/d' %s" % (self.searchfor, self.file))

    def replace(self):
        if self.backup == "yes":
            os_system("sed -i%s 's/%s/%s/p' %s && mv %s %s %s" % (self.backupfile, self.searchfor, self.replacewith, self.file, self.file, self.backupfile, self.backupdir))
        else:
            os_system("sed -i 's/%s/%s/p' %s" % (self.searchfor, self.replacewith, self.file))

    def add(self):
        # insert after linenr / search = linenr
        if self.backup == "yes":
            os_system("sed -i%s '%s a %s' %s && mv %s %s %s" % (self.backupfile, self.searchfor, self.replacewith, self.file, self.file, self.backupfile, self.backupdir))
        else:
            os_system("sed -i '%s a %s' %s" % (self.searchfor, self.replacewith, self.file))


# General
def ga_setup_pwd_gen(stringlength):
    chars = string_ascii_letters + string_digits + "!#-_"
    return ''.join(random_choice(chars) for i in range(stringlength))


# Searches nested keys for values -> gives back the name of the nested keys
def dict_nested_search(dictionary, tosearch):
    for key in dictionary:
        for subkey in dictionary[key]:
            if tosearch in subkey:
                return subkey
    return None


def string_check(string, maxlength=10, minlength=2):
    char_blacklist = "!%$§?^´`µ{}()°><|\\*ÄÖÜüöä@,"
    if type(string) != "str":
        return False
    elif len(string) > maxlength or len(string) < minlength:
        return False
    elif any((char in char_blacklist) for char in string):
        return False
    else:
        return True


def dict_keycheck(dictionary, dictkey):
    if dictionary[dictkey] is None:
        return False
    elif dictkey in dictionary:
        return True
    else:
        return False
