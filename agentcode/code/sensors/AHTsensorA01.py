#!/usr/bin/python3

import mysql.connector
import Adafruit_DHT
import sys
import inspect

from GA import MAINconfig
from GA import PATHconfig
from GA import CODEbase

sys.path.insert(0, PATHconfig.sensors)
import AHTdatacollect



#Basic Setup
sensor = "AHTA01"
pin = AHTdatacollect.AHTA01pin

##Logs
logfile = CODEbase.SENSORlogfile
currentscript = currentfile = inspect.getfile(inspect.currentframe())

logfile.write("\nSensor: " + sensor + "\n")

CODEbase.SENSORlogtime()
logfile.write("Script " + currentscript + ".\n")



#Check if Disabled
if any(x in sensor for x in MAINconfig.AHTdisabled):
        CODEbase.SENSORlogtime()
        logfile.write("This sensor was disabled via \"MAINconfig.py\".\n")
else:
	#DHT Data
	CODEbase.SENSORlogtime()
	logfile.write("Reading data from USB/serial connection to Arduino Uno (/dev/ttyACM0) .\n")

	CODEbase.SENSORlogtime()
	logfile.write("Reading sensor data.\n")

	datahumi,datatemp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, pin)

	CODEbase.SENSORlogtime()
	logfile.write("Sensor data received. Connecting to database " + MAINconfig.SENSORdatabase + ".\n")



	#DB Data
	CODEbase.SENSORlogtime()
	logfile.write("Connecting to database " + MAINconfig.SENSORdatabase + ".\n")

	GAdb = mysql.connector.connect(
	  host=MAINconfig.DATABASEserver,
	  user=MAINconfig.DATABASEuser,
	  passwd=MAINconfig.DATABASEpassword,
	  database=MAINconfig.SENSORdatabase
	)
	GAdbcursor = GAdb.cursor()

	CODEbase.SENSORlogtime()
	logfile.write("Connected to database.\n")



	#DB Data Insert
	sql = "INSERT INTO AHT (DATE, TIME, CONTROLLER, SENSOR, TEMPERATURE, HUMIDITY) VALUES (%s, %s, %s, %s, %s, %s)"
	val = (CODEbase.date01, CODEbase.time02, MAINconfig.controller, sensor, datatemp, datahumi)
	GAdbcursor.execute(sql, val)
	GAdb.commit()

	CODEbase.SENSORlogtime()
	logfile.write(str(GAdbcursor.rowcount) +  " line was inserted into the Database " + MAINconfig.SENSORdatabase + ".\n")
	CODEbase.SENSORlogtime()
	logfile.write("Row-ID:" + str(GAdbcursor.lastrowid) + ".\n")



	#DB Close
	GAdbcursor.close()
	GAdb.close()

	CODEbase.SENSORlogtime()
	logfile.write("Database connection was closed.\n")
