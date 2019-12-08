#!/usr/bin/python3

import inspect

from GA import MAINconfig
from GA import CODEbase



#Basic Setup
AHTA = MAINconfig.AHTAconnected
AHTApins = MAINconfig.AHTApins

##Logs
logfile = CODEbase.SENSORlogfile
currentscript = currentfile = inspect.getfile(inspect.currentframe())

CODEbase.SENSORlogtime()
logfile.write("Script " + currentscript + ".\n")

CODEbase.SENSORlogtime()
logfile.write("Preparing to read data.\n")



#AHT Setup
AHTAvar = []
for x in AHTA:
        y = x + "pin"
        AHTAvar.append(y)

for x, y in zip(AHTAvar,AHTApins):
        globals()[x] = y
