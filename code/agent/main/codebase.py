#!/usr/bin/python3

from datetime import datetime
import os
import string
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

def logpath(scripttype, output):
    scripttype = scripttype.lower()
    logdir = pathconfig.logs + scripttype + "/" + date02 + "/" + date03 + "/"
    if "dir" in output:
        return logdir
    elif "file" in output:
        return logdir + date04 + "_" + scripttype + ".log"
    else:
        raise SystemExit("\nInput Error. Either provide dir or file as second system argument.\nMust be exactly one.\n")

def logopen(scripttype):
    scripttype = scripttype.lower()
    logdir = logpath(scripttype, "dir")
    logfile = logpath(scripttype, "file")

    if os.path.exists(logdir) is False:
        os.system("mkdir -p " + logdir)
        return open(logfile, 'a')
    else:
        return open(logfile, 'a')

def logtime(scripttype):
    scripttype = scripttype.lower()
    logfile = logopen(scripttype)
    logfile.write(datetime.now().strftime("%H:%M:%S:%f") + " ")

#File operations
def deleteline(file, delete, backup = "no"):
    if backup == "yes":
        backupfile = "_" + date01 + "_" + time03 + ".bak
        backupdir = pathconfig.backup + codebase.date02 + "/" + codebase.date03 + "/" + codebase.date01
        os.system("sed -i" + backupfile + " '/" + delete + "/d' " + file + " && mv " + file + backupfile + " " + backupdir)
    else:
        os.system("sed -i '/" + delete + "/d' " + file)

def replaceline(file, replace, insert, backup = "no"):
    if backup == "yes":
        backupfile = "_" + date01 + "_" + time03 + ".bak
        backupdir = pathconfig.backup + codebase.date02 + "/" + codebase.date03 + "/" + codebase.date01
        os.system("sed -i" + backupfile + " 's/" + replace + "/" + insert + "/p' " + file + " && mv " + file + backupfile + " " + backupdir)
    else:
        os.system("sed -i 's/" + replace + "/" + insert + "/p' " + file)

def addline(file, linenr, insert, backup = "no"):
    #insert after linenr
    if backup == "yes":
        backupfile = "_" + date01 + "_" + time03 + ".bak
        backupdir = pathconfig.backup + codebase.date02 + "/" + codebase.date03 + "/" + codebase.date01
        os.system("sed -i" + backupfile + " '" + linenr + " a " + insert + "' " + file + " && mv " + file + backupfile + " " + backupdir)
    else:
        os.system("sed -i '" + linenr + " a " + insert + "' " + file)

#General
@lru_cache(maxsize=32)
def namegenletters(basename):
    namelist = []
    for letter in range(0, mainconfig.namemaxletters):
        tmpletter = string.ascii_lowercase[letter]
        namelist.append(basename + tmpletter)
    return namelist

@lru_cache(maxsize=32)
def namegen(basename, addon = ""):
    namelist = []
    for letter in range(0, mainconfig.namemaxletters):
        tmpletter = string.ascii_lowercase[letter]
        for number in range(1, mainconfig.namemaxnumbers):
            namelist.append(basename + tmpletter + "{:02d}".format(number) + addon)
    return namelist

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


#Actions

def actionblocksysargcheck(sysarg):
    #Check if actionblock was provided as system argument
    logfile = codebase.logopen("action")
    if mainconfig.loglevel >= 2:
        currentscript = currentfile = inspect.getfile(inspect.currentframe())
        codebase.logtime("action")
        logfile.write("Script " + currentscript + ".\n")

    with open(pathconfig.config + "mainconfig.py", 'r') as mainconfigfile:
        actionblockcount = mainconfigfile.read().count("actionblock")
        actionblocksysarglist = []
    if actionblockcount > 0:
        while actionblockcount > 0:
            actionblocknr = "actionblock{:02d}".format(actionblockcount)
            actionblockcount -= 1
            if actionblocknr in sysarg:
                actionblocksysarglist.append("actionblock{:02d}".format(actionblockcount))
                actionblock = actionblocknr
    else:
        if mainconfig.loglevel > 0:
            codebase.logtime("check")
            logfile.write("No actionblocks could be found in the configuration.\nConfiguration file:\n" + pathconfig.config + "mainconfig.py\n")

        raise SystemExit("\nNo actionblocks could be found in the configuration.\n")

    #Throw errors if system arguments were provided wrong
    if len(actionblocksysarglist) > 1:
        if mainconfig.loglevel > 0:
            codebase.logtime("action")
            logfile.write("Input Error. More than one actionblock was provided as system argument.\nMust be exactly one.\n")

        raise SystemExit("\nInput Error. More than one actionblock was provided as system argument.\nMust be exactly one.\n")

    elif len(actionblocksysarglist) < 1:
        if mainconfig.loglevel > 0:
            codebase.logtime("action")
            logfile.write("Input Error. No actionblock was provided as system argument.\nMust be exactly one.\n")

        raise SystemExit("\nInput Error. No actionblock was provided as system argument.\nMust be exactly one.\n")

    else:
        return print(actionblock)
