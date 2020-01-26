##!/usr/bin/python3

import os
import inspect

from GA import mainconfig
from GA import pathconfig
from GA import codebase

#log Setup
logfile = codebase.logopen("backup")

if mainconfig.loglevel > 0:
    currentscript = inspect.getfile(inspect.currentframe())

    codebase.logtime("backup")
    logfile.write("Script " + currentscript + ".\n")

# Backup if enabled
if mainconfig.backupenabled == "yes":
    backupdir = pathconfig.backup + codebase.date02 + "/" + codebase.date03 + "/" + codebase.date01
    if mainconfig.loglevel > 0:
        codebase.logtime("backup")
        logfile.write("Starting backup.\n")

    # Backup preparations
    if os.path.exists(pathconfig.backupdir) is False:
        os.system("mkdir -p " + backupdir)

    if mainconfig.loglevel >= 2:
        codebase.logtime("backup")
        logfile.write("Backup directories exist/were created.\n")

    # Backup
    os.system("mysqldump -u gabackup --all-databases > " + backupdir + "/ga_databases_dump.sql")

    # Backup logs if enabled
    if mainconfig.backuplogs == "yes" and pathconfig.logs.find(pathconfig.root) < 0:
        os.system("cp -r " + pathconfig.logs + " " + backupdir)

    if mainconfig.loglevel >= 2:
        codebase.logtime("backup")
        logfile.write("Backup Finished.\n")

elif mainconfig.backupenabled == "no" and mainconfig.loglevel >= 0:
    codebase.logtime("backup")
    logfile.write("Backup was disabled.\n")