#!/usr/bin/python3

from datetime import datetime
from time import strftime


#Time Setup
date01 = datetime.now().strftime("%Y-%m-%d")
date02 = datetime.now().strftime("%Y")
date03 = datetime.now().strftime("%m")



#Growautomation File-Path Configuration

#General
root = "/etc/growautomation/"
logs = "/var/log/growautomation/"
backup = "/mnt/growautomation/backup/"
code = root + "code/"



#Sensors
sensors = code + "sensors/"

SENSORlogs01 = logs + "SENSORS/"
SENSORlogs02 = SENSORlogs01 + date02 + "/" + date03
SENSORlogs = SENSORlogs02 + "/SENSOR_" + date01 + ".log"

##Files
#SENSORlogheader = sensors + "SENSORlogheader.py"
SENSOReh = sensors + "EHsensor*.py"
SENSORaht = sensors + "AHTsensor*.py"


#Acions
actions = code + "actions/"

ACTIONlogs01 = logs + "ACTIONS/"
ACTIONlogs02 = ACTIONlogs01 + date02 + "/" + date03
ACTIONlogs = ACTIONlogs02 + "/ACTION_" + date01 + ".log"

##Files
#ACTIONlogheader = actions + "ACTIONlogheader.py"



#Checks
checks = code + "checks/"

CHECKlogs01 = logs + "CHECKS/"
CHECKlogs02 = CHECKlogs01 + date02 + "/" + date03
CHECKlogs = CHECKlogs02 + "/CHECK_" + date01 + ".log"

##Files
CHECKlogheader = checks + "CHECKlogheader.py"
CHECKeh = checks + "EHcheck.py"

##Scripting
CHECKehaction = actions + "PSU01-OL01.py"
CHECKehreverse = CHECKehaction



#Backups
BACKUPlogs01 = logs + "BACKUP/"
BACKUPlogs02 = BACKUPlogs01 + date02 + "/" + date03
BACKUPlogs = BACKUPlogs02 + "/BACKUP_" + date01 + ".log"

Backupdir = backup + date02 + "/" + date03 + "/" + date01
