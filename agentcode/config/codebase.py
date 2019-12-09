#!/usr/bin/python3

from datetime import datetime
import os
import sys

from GA import pathconfig


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

#actions

def actionblocksysargcheck(sysarg):
    # Check if actionblock was provided as system argument
    with open(pathconfig.config + "mainconfig.py", 'r') as mainconfigfile:
        actionblockcount = mainconfigfile.read().count("actionblock")
    actionblocksysarglist = []
    while actionblockcount > 0:
        actionblocknr = "actionblock{:02d}".format(actionblockcount)
        actionblockcount -= 1
        if actionblocknr in sysarg:
            actionblocksysarglist.append("actionblock{:02d}".format(actionblockcount))
            actionblock = actionblocknr

    # Throw errors if system arguments were provided wrong
    if len(actionblocksysarglist) > 1:
        return sys.exit("\nInput Error. More than one actionblock was provided as system argument.\nMust be exactly one.")
    elif len(actionblocksysarglist) < 1:
        return sys.exit("\nInput Error. No actionblock was provided as system argument.\nMust be exactly one.")
    else:
        return print(actionblock)
