#!/usr/bin/python3

from datetime import datetime
import os
import sys
import string
import collections.abc

from GA import pathconfig


#Time

time01 = datetime.now().strftime("%H-%M-%S")
time02 = datetime.now().strftime("%H:%M:%S")
time03 = datetime.now().strftime("%H-%M")

date01 = datetime.now().strftime("%Y-%m-%d")
date02 = datetime.now().strftime("%Y")
date03 = datetime.now().strftime("%m")
date04 = datetime.now().strftime("%d")

# Logs

def logpath(scripttype, output):
    scripttype = scripttype.lower()
    logdir = pathconfig.logs + scripttype + "/" + date02 + "/" + date03 + "/"
    if "dir" in output:
        return logdir
    elif "file" in output:
        return logdir + date04 + "_" + scripttype + ".log"
    else:
        return sys.exit("\nInput Error. Either provide dir or file as second system argument.\nMust be exactly one.")

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

# General

def namegen(basename, addon = "", letterrange = 3, numberrange = 100):
    namelist = []
    for letter in range(0, letterrange):
        tmpletter = string.ascii_lowercase[letter]
        for number in range(1, numberrange):
            namelist.append(basename + tmpletter + "{:02d}".format(number) + addon)
    return namelist

#def dictnestupdate( ):
#    def update(d, u):
#        for k, v in u.items():
#            if isinstance(v, collections.abc.Mapping):
#                d[k] = update(d.get(k, {}), v)
#            else:
#                d[k] = v
#        return d

# Searches nested keys for values -> gives back the name of the nested keys
def dictnestsearch(dict, tosearch):
    for k in dict:
        for v in dict[k]:
            if tosearch in v:
                return k
    return None


#Actions

def actionblocksysargcheck(sysarg):
    # Check if actionblock was provided as system argument
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

        sys.exit("\nNo actionblocks could be found in the configuration.")

    # Throw errors if system arguments were provided wrong
    if len(actionblocksysarglist) > 1:
        if mainconfig.loglevel > 0:
            codebase.logtime("action")
            logfile.write("Input Error. More than one actionblock was provided as system argument.\nMust be exactly one.\n")

        return sys.exit("\nInput Error. More than one actionblock was provided as system argument.\nMust be exactly one.")

    elif len(actionblocksysarglist) < 1:
        if mainconfig.loglevel > 0:
            codebase.logtime("action")
            logfile.write("Input Error. No actionblock was provided as system argument.\nMust be exactly one.\n")

        return sys.exit("\nInput Error. No actionblock was provided as system argument.\nMust be exactly one.")

    else:
        return print(actionblock)
