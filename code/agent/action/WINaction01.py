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

#DC Motor 62RPM

from time import sleep
import mysql.connector
import RPi.GPIO as GPIO

import inspect
import sys

from GA import MAINconfig
from GA import CODEbase
from GA import PATHconfig

sys.path.insert(0, PATHconfig.actions)
import WINdatacollect



#Basic Setup
sensor = "WIN01"
ACTIONtaken = "Opened and Closed"

##WIN
PIN1 = WINdatacollect.WIN01pinfwd
PIN2 = WINdatacollect.WIN01pinrev
PINp = int(PIN1)
PINn = int(PIN2)

WINopentime = MAINconfig.WINopentime
WINruntime = 5

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PINp, GPIO.OUT)
GPIO.setup(PINp, GPIO.OUT, initial=0)
GPIO.setup(PINn, GPIO.OUT)
GPIO.setup(PINn, GPIO.OUT, initial=0)

##Logs
logfile = CODEbase.ACTIONlogfile
currentscript = currentfile = inspect.getfile(inspect.currentframe())

CODEbase.ACTIONlogtime()
logfile.write("Script " + currentscript + ".\n")

CODEbase.ACTIONlogtime()
logfile.write("Starting Window-Opener.\n")



#WIN
##Opening
CODEbase.ACTIONlogtime()
logfile.write("Opening Window.\n")

GPIO.output(PINp, 1)
sleep(WINruntime)
GPIO.output(PINp, 0)

##Leaving Open
sleep(WINopentime)

##Closing
CODEbase.ACTIONlogtime()
logfile.write("Closing Window.\n")

GPIO.output(PINn, 1)
sleep(WINruntime)
GPIO.output(PINn, 0)



#Log to Database
GAdb = mysql.connector.connect(
  host=MAINconfig.DATABASEserver,
  user=MAINconfig.DATABASEuser,
  passwd=MAINconfig.DATABASEpassword,
  database=MAINconfig.ACTIONdatabase
)
GAdbcursor = GAdb.cursor()

CODEbase.ACTIONlogtime()
logfile.write("Connected to database " + MAINconfig.ACTIONdatabase + ".\n")

sql = "INSERT INTO WIN (DATE, TIME, CONTROLLER, SENSOR, ACTIONTAKEN, ACTIONTIME) VALUES (%s, %s, %s, %s, %s, %s)"
val = (CODEbase.date01, CODEbase.time02, MAINconfig.controller, sensor, ACTIONtaken, WINopentime)
GAdbcursor.execute(sql, val)
GAdb.commit()

CODEbase.ACTIONlogtime()
logfile.write(str(GAdbcursor.rowcount) +  " line was inserted into the Database " + MAINconfig.ACTIONdatabase + ".\n")
CODEbase.ACTIONlogtime()
logfile.write("Row-ID:" + str(GAdbcursor.lastrowid) + ".\n")

GAdbcursor.close()
GAdb.close()

CODEbase.ACTIONlogtime()
logfile.write("Database connection was closed.\n")
