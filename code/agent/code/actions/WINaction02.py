#!/usr/bin/python3
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
sensor = "WIN02"
ACTIONtaken = "Opened and Closed"

##WIN
PIN1 = WINdatacollect.WIN02pinfwd
PIN2 = WINdatacollect.WIN02pinrev
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
