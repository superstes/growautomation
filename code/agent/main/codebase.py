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

#ga_version0.1

from datetime import datetime
import os
from string import ascii_letters as string_ascii_letters
from string import ascii_lowercase as string_ascii_lowercase
from string import digits as string_digits
from random import choice as random_choice
from functools import lru_cache

from GA import pathconfig
from GA import mainconfig


#Time

time01 = datetime.now().strftime("%H-%M-%S")
time02 = datetime.now().strftime("%H:%M:%S")
time03 = datetime.now().strftime("%H-%M")

date01 = datetime.now().strftime("%Y-%m-%d")
date02 = datetime.now().strftime("%Y")
date03 = datetime.now().strftime("%m")
date04 = datetime.now().strftime("%d")

#Logs
def ga_log(scripttype, output, loglevel=""):
    scripttype = scripttype.lower()
    def logpath(scripttype, check):
        logdir = pathconfig.logs + scripttype + "/" + date02 + "/" + date03 + "/"
        if "dir" in check:
            return logdir
        elif "file" in check:
            return logdir + date04 + "_" + scripttype + ".log"
        else:
            raise SystemExit("\nInput Error. Either provide dir or file as second system argument.\nMust be exactly one.\n")

    def logopen(scripttype):
        logdir = logpath(scripttype, "dir")
        logfile = logpath(scripttype, "file")

        if os.path.exists(logdir) is False:
            os.system("mkdir -p " + logdir)
            return open(logfile, 'a')
        else:
            return open(logfile, 'a')

    def logwrite(scripttype, output, loglevel):
        def write():
            logfile = logopen(scripttype)
            logfile.write(datetime.now().strftime("%H:%M:%S:%f") + " ")
            logfile.write("%s.\n" % output)
            logfile.close()
        if loglevel != "":
            if loglevel > mainconfig.loglevel:
                return False
            else:
                write()
        else:
            write()
    logwrite(*args, **kwargs)

#File operations
def deleteline(file, delete, backup = "no"):
    if backup == "yes":
        backupfile = "_" + date01 + "_" + time03 + ".bak
        backupdir = pathconfig.backup + date02 + "/" + date03 + "/" + date01
        os.system("sed -i" + backupfile + " '/" + delete + "/d' " + file + " && mv " + file + backupfile + " " + backupdir)
    else:
        os.system("sed -i '/" + delete + "/d' " + file)

def replaceline(file, replace, insert, backup = "no"):
    if backup == "yes":
        backupfile = "_" + date01 + "_" + time03 + ".bak
        backupdir = pathconfig.backup + date02 + "/" + date03 + "/" + date01
        os.system("sed -i" + backupfile + " 's/" + replace + "/" + insert + "/p' " + file + " && mv " + file + backupfile + " " + backupdir)
    else:
        os.system("sed -i 's/" + replace + "/" + insert + "/p' " + file)

def addline(file, linenr, insert, backup = "no"):
    #insert after linenr
    if backup == "yes":
        backupfile = "_" + date01 + "_" + time03 + ".bak
        backupdir = pathconfig.backup + date02 + "/" + date03 + "/" + date01
        os.system("sed -i" + backupfile + " '" + linenr + " a " + insert + "' " + file + " && mv " + file + backupfile + " " + backupdir)
    else:
        os.system("sed -i '" + linenr + " a " + insert + "' " + file)

#General
@lru_cache(maxsize=32)
def namegenletters(basename):
    namelist = []
    for letter in range(0, mainconfig.namemaxletters):
        tmpletter = string_ascii_lowercase[letter]
        namelist.append(basename + tmpletter)
    return namelist

@lru_cache(maxsize=32)
def namegen(basename, addon = ""):
    namelist = []
    for letter in range(0, mainconfig.namemaxletters):
        tmpletter = string_ascii_lowercase[letter]
        for number in range(1, mainconfig.namemaxnumbers):
            namelist.append(basename + tmpletter + "{:02d}".format(number) + addon)
    return namelist

def pwdgen(stringLength):
    chars = string_ascii_letters + string_digits + "!#-_"
    return ''.join(random_choice(chars) for i in range(stringLength))

#Searches nested keys for values -> gives back the name of the nested keys
def dictnestsearch(dict, tosearch):
    for k in dict:
        for v in dict[k]:
            if tosearch in v:
                return k
    return None

#Sensors

def sensorenabledcheck(sensortype):
    with open(pathconfig.config + "mainconfig.py", 'r') as mainconfigfile:
        sensorsenabled = 0
        sensornamelist = namegenletters(sensortype)
        for sensorname in sensornamelist:
            try:
                tmpsensorconnected = len(getattr(mainconfig, sensorname + "connected").keys())
                sensorsenabled += tmpsensorconnected
                tmpsensordisabled = len(getattr(mainconfig, sensorname + "disabled"))
                sensorsenabled -= tmpsensordisabled
            except AttributeError:
                pass
        return sensorsenabled


# Actions
#
# def actionblocksysargcheck(sysarg):
#     #Check if actionblock was provided as system argument
#     logfile = logopen("action")
#     if mainconfig.loglevel >= 2:
#         currentscript = currentfile = inspect.getfile(inspect.currentframe())
#         logtime("action")
#         logfile.write("Script " + currentscript + ".\n")
#
#     with open(pathconfig.config + "mainconfig.py", 'r') as mainconfigfile:
#         actionblockcount = mainconfigfile.read().count("actionblock")
#         actionblocksysarglist = []
#     if actionblockcount > 0:
#         while actionblockcount > 0:
#             actionblocknr = "actionblock{:02d}".format(actionblockcount)
#             actionblockcount -= 1
#             if actionblocknr in sysarg:
#                 actionblocksysarglist.append("actionblock{:02d}".format(actionblockcount))
#                 actionblock = actionblocknr
#     else:
#         if mainconfig.loglevel > 0:
#             logtime("check")
#             logfile.write("No actionblocks could be found in the configuration.\nConfiguration file:\n" + pathconfig.config + "mainconfig.py\n")
#
#         raise SystemExit("\nNo actionblocks could be found in the configuration.\n")
#
#     #Throw errors if system arguments were provided wrong
#     if len(actionblocksysarglist) > 1:
#         if mainconfig.loglevel > 0:
#             logtime("action")
#             logfile.write("Input Error. More than one actionblock was provided as system argument.\nMust be exactly one.\n")
#
#         raise SystemExit("\nInput Error. More than one actionblock was provided as system argument.\nMust be exactly one.\n")
#
#     elif len(actionblocksysarglist) < 1:
#         if mainconfig.loglevel > 0:
#             logtime("action")
#             logfile.write("Input Error. No actionblock was provided as system argument.\nMust be exactly one.\n")
#
#         raise SystemExit("\nInput Error. No actionblock was provided as system argument.\nMust be exactly one.\n")
#
#     else:
#         return print(actionblock)
