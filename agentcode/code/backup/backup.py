##!/usr/bin/python3

import os
import inspect

from GA import MAINconfig
from GA import PATHconfig
from GA import CODEbase

#Log Setup
logfile = CODEbase.BACKUPlogfile

if MAINconfig.LOGlevel > 0:
    currentscript = inspect.getfile(inspect.currentframe())

    CODEbase.SENSORlogtime()
    logfile.write("\nScript " + currentscript + ".\n")

#Backup if enabled
if MAINconfig.BACKUPenabled == "YES":
    if MAINconfig.LOGlevel > 0:
        CODEbase.BACKUPlogtime()
        logfile.write("Starting Backup.\n")

    #Backup Preperations
    if os.path.exists(PATHconfig.BACKUPdir) is False:
        os.system("mkdir -p " + Backupdir)

    if MAINconfig.LOGlevel >= 2:
        CODEbase.BACKUPlogtime()
        logfile.write("Backup directories exist/were created.\n")

    #Backup
    os.system("cp -r " + PATHconfig.root + " " + backupfolder)

    if MAINconfig.LOGbackup == "YES":
        os.system("cp -r " + PATHconfig.logs + " " + backupfolder)

    if MAINconfig.LOGlevel >= 2:
        CODEbase.BACKUPlogtime()
        logfile.write("Backup Finished.\n\n")

elif MAINconfig.BACKUPenabled == "NO" and MAINconfig.LOGlevel >= 0:
    CODEbase.BACKUPlogtime()
    logfile.write("Backup was disabled.\n\n")