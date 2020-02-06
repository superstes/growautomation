#!/usr/bin/python3

import inspect

from GA import MAINconfig
from GA import CODEbase



#Basic Setup

##Logs
#logfile = CODEbase.ACTIONlogfile
#currentscript = currentfile = inspect.getfile(inspect.currentframe())

#CODEbase.ACTIONlogtime()
#logfile.write("Script " + currentscript + ".\n")

#CODEbase.ACTIONlogtime()
#logfile.write("Preparing to read data.\n")



#Data Collection
WINpinfwd = []
for x in MAINconfig.WINconnected:
        y = x + "pinfwd"
        WINpinfwd.append(y)

for x, y in zip(WINpinfwd,MAINconfig.WINpinfwd):
        globals()[x] = y

WINpinrev = []
for x in MAINconfig.WINconnected:
        y = x + "pinrev"
        WINpinrev.append(y)

for x, y in zip(WINpinrev,MAINconfig.WINpinrev):
        globals()[x] = y
