#!/usr/bin/python3

import mysql.connector
from time import sleep
import os
import inspect
import sys

from GA import MAINconfig
from GA import PATHconfig
from GA import CODEbase


# Logs
logfile = CODEbase.CHECKlogfile
if MAINconfig.LOGlevel > 0:
currentscript = currentfile = inspect.getfile(inspect.currentframe())
	CODEbase.CHECKlogtime()
	logfile.write("Script " + currentscript + ".\n")

if MAINconfig.LOGlevel >= 2:
	CODEbase.CHECKlogtime()
	logfile.write("Connecting to database " + MAINconfig.SENSORdatabase + ".\n")

# DB Data
DB = mysql.connector.connect(
	host=MAINconfig.DATABASEserver,
	user=MAINconfig.DATABASEuser,
	passwd=MAINconfig.DATABASEpassword,
	database=MAINconfig.SENSORdatabase
)


if "EH" in sys.argv:
	SENSORconnected = getattr(MAINconfig, "EHABconnected")
	SENSORdisabled = getattr(MAINconfig, "EHABdisabled")

elif "AHT" in sys.argv:
	SENSORconnected = getattr(MAINconfig, "AHTAconnected")
	SENSORdisabled = getattr(MAINconfig, "AHTAdisabled")
else:
	sys.exit("\nInput Error. Sensortype has to be provided as system argument.\n\nExample:\npython3 " + currentscript + " EH")

SENSORSenabled = 0
for x in SENSORconnected:
	if x not in SENSORdisabled:
		SENSORSenabled += 1


def actioncheck(action, ACTIONblocknr):
	# Data Query
	DBcursor = DB.cursor()
	if MAINconfig.LOGlevel >= 2:
		CODEbase.CHECKlogtime()
		logfile.write("Connected to database.\n")

	DBdataquery = "SELECT * FROM " + sys.argv[1] + " ORDER BY ID DESC LIMIT " + str(
		SENSORSenabled * MAINconfig.CHECKrange)
	DBcursor.execute(DBdataquery)
	DBdata01 = []
	for row in DBcursor:
		DBdata01.append(float(row[MAINconfig.CHECKdbdatacolumn]))
	ACTIONstate = str((sum(dbdata01)) / MAINconfig.CHECKrange)

	GAdbcursor.close()
	GAdb.close()

	if MAINconfig.LOGlevel >= 2:
		CODEbase.CHECKlogtime()
		logfile.write("Data from database collected.\n")
		CODEbase.CHECKlogtime()
		logfile.write("Database connection was closed.\n")

	# Action Check
	print("DO multiple " + action + " ACTION NAUW")
	ACTIONpoint = getattr(MAINconfig, action + "activation")
	ACTIONtime = getattr(MAINconfig, action + "time")

	if MAINconfig.LOGlevel >= 2:
		CODEbase.CHECKlogtime()
		logfile.write("Current state is: " + ACTIONstate + ".\n")
		CODEbase.CHECKlogtime()
		logfile.write("Current activationpoint is: " + ACTIONpoint + ".\n")

	if ACTIONstate < ACTIONpoint:
		# Action
		scriptstartpath = getattr(PATHconfig, action + "actionstartpath")
		#scriptstoppath = getattr(PATHconfig, action + "actionstoppath")

		if MAINconfig.LOGlevel > 0:
			CODEbase.CHECKlogtime()
			logfile.write("Action needed - starting script " + scriptstartpath + ".\n")

		os.system("/usr/bin/python3 " + scriptstartpath + " " + ACTIONblocknr)

		#if MAINconfig.LOGlevel >= 2:
		#	CODEbase.CHECKlogtime()
		#	logfile.write("Script " + currentscript + ".\n")
		#	CODEbase.CHECKlogtime()
		#	logfile.write("Action will be reversed after " + str(ACTIONtime) + " seconds.\n")

		#sleep(ACTIONtime)

		#if MAINconfig.LOGlevel > 0:
		#	CODEbase.CHECKlogtime()
		#	logfile.write("Reversing Action - starting script  " + scriptstoppath + ".\n")

		#os.system("/usr/bin/python3 " + scriptstoppath)

		#if MAINconfig.LOGlevel >= 2:
		#	CODEbase.CHECKlogtime()
		#	logfile.write("Script " + currentscript + ".\n")

		#if MAINconfig.LOGactiontodb == "YES":
			# Log to DB

		#	DBcursor = DB.cursor()

		#	if MAINconfig.LOGlevel >= 2:
		#		CODEbase.CHECKlogtime()
		#		logfile.write("Connected to database " + MAINconfig.ACTIONdatabase + ".\n")

		#	sql = "INSERT INTO ACTIONS (DATE, TIME, CONTROLLER, SENSOR, ACTIONTAKEN, ACTIONSTATE, ACTIONPOINT) VALUES (%s, %s, %s, %s, %s, %s, %s)"
		#	val = (
		#		CODEbase.date01, CODEbase.time01, MAINconfig.controller, sys.argv[1], action, ACTIONstate,
		#		MAINconfig.PUMPactivation)
		#	DBcursor.execute(sql, val)
		#	DB.commit()

		#	if MAINconfig.LOGlevel >= 2:
		#		CODEbase.CHECKlogtime()
		#		logfile.write(
		#			str(DBcursor.rowcount) + " line was inserted into the Database " + MAINconfig.ACTIONdatabase + ".\n")
		#		CODEbase.CHECKlogtime()
		#		logfile.write("Row-ID:" + str(DBcursor.lastrowid) + ".\n")

		#	DBcursor.close()
		#	DB.close()

		#	if MAINconfig.LOGlevel >= 2:
		#		CODEbase.CHECKlogtime()
		#		logfile.write("Database connection was closed.\n")
			if MAINconfig.LOGlevel > 0:
				CODEbase.SENSORlogtime()
				logfile.write("Check was processed.\n")

	else:
		if MAINconfig.LOGlevel > 0:
			CODEbase.CHECKlogtime()
			logfile.write("No action needed.\n")



if SENSORSenabled > 0:
	with open(PATHconfig.root + "config/MAINconfig.py", 'r') as MAINconfigfile:
		whilecount = MAINconfigfile.read().count("ACTIONblock")
	while whilecount > 0:
		#Check if sensor is in the current actionblock
		ACTIONblock = getattr(MAINconfig, "ACTIONblock{:02d}".format(whilecount))
		ACTIONblocknr = "ACTIONblock{:02d}".format(whilecount)
		whilecount -= 1
		#print(whilecount + " " + ACTIONblock)
		SENSORcount = str(ACTIONblock).count(sys.argv[1])-1
		if SENSORcount > 0:
			#Check if action is required
			#Check which actions are linked to the current sensor
			ACTIONtypes = MAINconfig.ACTIONtypes.get(sys.argv[1])
			ACTIONtypecount = len(ACTIONtypes.split())
			if ACTIONtypecount > 1:
				for action in ACTIONtypes:
					SENSORactioncount = str(ACTIONblock).count(action)
					#Check if actions are in the current actionblock
					if SENSORactioncount > 0:
						actioncheck(action, ACTIONblocknr)
					else:
						print("Action " + action + " isn't in the current actionblock")
			else:
				SENSORactioncount = str(ACTIONblock).count(ACTIONtypes)
				#Check if action is in the current actionblock
				if SENSORactioncount > 0:
					actioncheck(ACTIONtypes, ACTIONblocknr)
				else:
					print("Action " + ACTIONtypes + " isn't in the current actionblock")

		else:
			print("The sensor isn't in the current actionblock")