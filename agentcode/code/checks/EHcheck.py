#!/usr/bin/python3

import mysql.connector
from time import sleep
import os
import inspect
import sys

from GA import MAINconfig
from GA import PATHconfig
from GA import CODEbase



#Basic Setup
sensor = "EH"

##DB
EHconnected = len(MAINconfig.EHAconnected) + len(MAINconfig.EHBconnected)
DBDATAtablerow = int("4")							#row containing the sensor data	-> counted from left without counting the ID row
DBDATAquant = EHconnected * int("6")						#Defines the number of rows to use in the average calculation
										#Nr. of sensors x number of rows per sensor (in this case we check the last hour)
##Action
ACTIONpoint = str(MAINconfig.PUMPactivation) 					#when should the action be started
ACTIONtime = int(MAINconfig.PUMPtime)						#how log should the action be active
ACTIONtaken = "PSU01-OL01 powerstate changed"					#message to log to sql if action is taken

##Logs
logfile = CODEbase.CHECKlogfile
currentscript = currentfile = inspect.getfile(inspect.currentframe())

CODEbase.CHECKlogtime()
logfile.write("Script " + currentscript + ".\n")

CODEbase.CHECKlogtime()
logfile.write("Connecting to database " + MAINconfig.SENSORdatabase + ".\n")



#DB Data
GAdb = mysql.connector.connect(
  host=MAINconfig.DATABASEserver,
  user=MAINconfig.DATABASEuser,
  passwd=MAINconfig.DATABASEpassword,
  database=MAINconfig.SENSORdatabase
)
GAdbcursor = GAdb.cursor()

CODEbase.CHECKlogtime()
logfile.write("Connected to database.\n")



#Data Select
DBDATAquery = "SELECT * FROM EH ORDER BY ID DESC LIMIT " + str(DBDATAquant)
GAdbcursor.execute(DBDATAquery)


dbdata01 = []
for row in GAdbcursor:
	dbdata01.append(float(row[DBDATAtablerow]))
dbdata02 = sum(dbdata01)
dbdata03 = dbdata02 / DBDATAquant
ACTIONstate = str(dbdata03)


GAdbcursor.close()
GAdb.close()

CODEbase.CHECKlogtime()
logfile.write("Data from database collected.\n")
CODEbase.CHECKlogtime()
logfile.write("Current state is: " + ACTIONstate + ".\n")
CODEbase.CHECKlogtime()
logfile.write("Point of Action is currently set to: " + ACTIONpoint + ".\n")
CODEbase.CHECKlogtime()
logfile.write("Database connection was closed.\n")



#Action
if ACTIONstate < ACTIONpoint:
	CODEbase.CHECKlogtime()
	logfile.write("Action needed - starting script " + PATHconfig.CHECKehaction + ".\n\n")

	os.system("/usr/bin/python3 " + PATHconfig.CHECKehaction)


	CODEbase.CHECKlogtime()
	logfile.write("Script " + currentscript + ".\n")

	CODEbase.CHECKlogtime()
	logfile.write("Action will be reversed after " + str(ACTIONtime) + " seconds.\n")

	sleep(ACTIONtime)


	CODEbase.CHECKlogtime()
	logfile.write("Reversing Action - starting script  " + PATHconfig.CHECKehreverse + ".\n\n")

	os.system("/usr/bin/python3 " + PATHconfig.CHECKehreverse)


	CODEbase.CHECKlogtime()
	logfile.write("Script " + currentscript + ".\n")
else:
	CODEbase.CHECKlogtime()
	logfile.write("No action needed.\n")



#Log to Database
GAdb = mysql.connector.connect(
  host=MAINconfig.DATABASEserver,
  user=MAINconfig.DATABASEuser,
  passwd=MAINconfig.DATABASEpassword,
  database=MAINconfig.ACTIONdatabase
)
GAdbcursor = GAdb.cursor()

CODEbase.CHECKlogtime()
logfile.write("Connected to database " + MAINconfig.ACTIONdatabase + ".\n")

sql = "INSERT INTO ACTIONS (DATE, TIME, CONTROLLER, SENSOR, ACTIONTAKEN, ACTIONSTATE, ACTIONPOINT) VALUES (%s, %s, %s, %s, %s, %s, %s)"
val = (CODEbase.date01, CODEbase.time01, MAINconfig.controller, sensor, ACTIONtaken, ACTIONstate, ACTIONpoint)
GAdbcursor.execute(sql, val)
GAdb.commit()

CODEbase.CHECKlogtime()
logfile.write(str(GAdbcursor.rowcount) +  " line was inserted into the Database " + MAINconfig.ACTIONdatabase + ".\n")
CODEbase.CHECKlogtime()
logfile.write("Row-ID:" + str(GAdbcursor.lastrowid) + ".\n")

GAdbcursor.close()
GAdb.close()

CODEbase.CHECKlogtime()
logfile.write("Database connection was closed.\n\n\n")
