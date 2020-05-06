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
    os.system("mysqldump -u gabackup --all-databases | gzip -9 > " + backupdir + "/ga_databases_dump.sql.gz")

    if mainconfig.loglevel >= 2:
        codebase.logtime("backup")
        logfile.write("Backup Finished.\n")

elif mainconfig.backupenabled == "no" and mainconfig.loglevel >= 0:
    codebase.logtime("backup")
    logfile.write("Backup was disabled.\n")