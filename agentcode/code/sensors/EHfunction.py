#!/usr/bin/python3

import serial
import sys
import inspect
import mysql.connector

from GA import MAINconfig
from GA import PATHconfig
from GA import CODEbase

sys.path.insert(0, PATHconfig.sensors)


#Basic Setup



#Log Setup
logfile = CODEbase.SENSORlogfile

if MAINconfig.LOGlevel > 0:
	currentscript = inspect.getfile(inspect.currentframe())

	CODEbase.SENSORlogtime()
	logfile.write("\nScript " + currentscript + ".\n")



#Functions

def EHDataCollection(SensorType):
	#Basic Setup
	if SensorType == "A":
		EHcon = MAINconfig.EHAconnected
		EHdis = MAINconfig.EHAdisabled

	if SensorType == "B":
		EHcon = MAINconfig.EHBconnected
		EHdis = MAINconfig.EHBdisabled

	EHen = (list(set(EHcon) - set(EHdis)))

	#Disable Check
	if MAINconfig.LOGlevel >= 2:
		if not EHdis or " " in EHdis:
			CODEbase.SENSORlogtime()
			logfile.write("No sensors were disabled via the \"MAINconfig\" .\n")
	else:
		CODEbase.SENSORlogtime()
		logfile.write("The following sensors were disabled via the \"MAINconfig\": " + EHdis + " \n")

	#Get Data
	if MAINconfig.LOGlevel >= 2:
		CODEbase.SENSORlogtime()
		logfile.write("Processing data-type " + DataType + " for sensor-type " + SensorType + " .\n")

	EHSerialRead = serial.Serial('/dev/ttyACM0',9600)
	EHSerialDataBin = EHSerialRead.readline()

	if MAINconfig.LOGlevel >= 2:
		CODEbase.SENSORlogtime()
		logfile.write("Sensor Data Received. Starting Data Processing.\n")

	#Prepare Data for Processing
	EHSerialData = EHSerialDataBin.decode('utf-8')
	EHSerialDataStrip = EHSerialData.strip()
	EHAData,EHBData = EHSerialDataStrip.split(";")

	if SensorType == "A":
		EHDataPerRaw,EHDataDecRaw = EHAData.split("-")

	elif SensorType == "B":
		EHDataPerRaw,EHDataDecRaw = EHBData.split("-")

	EHDataPerSplit = EHDataPerRaw.split(",")
	EHDataDecSplit = EHDataDecRaw.split(",")

	if MAINconfig.LOGlevel >= 2:
		CODEbase.SENSORlogtime()
		logfile.write("Data Processing finished. Ready for Import.\n")

	if MAINconfig.LOGlevel >= 2:
		CODEbase.SENSORlogtime()
		logfile.write("Connecting to database " + MAINconfig.SENSORdatabase + ".\n")

	#DB Setup
	GAdb = mysql.connector.connect(
	  host=MAINconfig.DATABASEserver,
	  user=MAINconfig.DATABASEuser,
	  passwd=MAINconfig.DATABASEpassword,
	  database=MAINconfig.SENSORdatabase
	)

	GAdbcursor = GAdb.cursor()

	if MAINconfig.LOGlevel >= 2:
		CODEbase.SENSORlogtime()
		logfile.write("Connected to database.\n")

	for x in EHen:
		sensor = x
		data = 

		#DB Data Import
		sql = "INSERT INTO EH (DATE, TIME, CONTROLLER, SENSOR, HUMIDITY, HUMIDITYDEC) VALUES (%s, %s, %s, %s, %s, %s)"
		val = (CODEbase.date01, CODEbase.time02, MAINconfig.controller, sensor, data, datadec)
		GAdbcursor.execute(sql, val)
		GAdb.commit()

		if MAINconfig.LOGlevel >= 2:
			CODEbase.SENSORlogtime()
			logfile.write(str(GAdbcursor.rowcount) +  " line was inserted into the Database " + MAINconfig.SENSORdatabase + ".\n")

			CODEbase.SENSORlogtime()
			logfile.write("Row-ID:" + str(GAdbcursor.lastrowid) + ".\n")

	#DB Close
	GAdbcursor.close()
	GAdb.close()

	if MAINconfig.LOGlevel >= 2:
		CODEbase.SENSORlogtime()
		logfile.write("Database connection was closed.\n")

	if MAINconfig.LOGlevel > 0:
		CODEbase.SENSORlogtime()
		logfile.write("Data for sensor " + sensor + " was imported.\n")
