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
