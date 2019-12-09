#!/usr/bin/python3

import mysql.connector
import os
import inspect
import sys

from GA import mainconfig
from GA import pathconfig
from GA import codebase


# logs
logfile = codebase.logopen("check")
if mainconfig.loglevel > 0:
currentscript = currentfile = inspect.getfile(inspect.currentframe())
	codebase.logtime("check")
	logfile.write("Script " + currentscript + ".\n")

# System arguments
if "eh" in sys.argv:
	sensorconnected = getattr(mainconfig, "ehabconnected")
	sensordisabled = getattr(mainconfig, "ehabdisabled")

elif "aht" in sys.argv:
	sensorconnected = getattr(mainconfig, "ahtaconnected")
	sensordisabled = getattr(mainconfig, "ahtadisabled")
else:
	sys.exit("\nInput Error. Sensortype has to be provided as system argument.\n\nExample:\npython3 " + currentscript + " EH")

sensorsenabled = 0
for x in sensorconnected:
	if x not in sensordisabled:
		sensorsenabled += 1


def actioncheck(action, actionblocknr):
	# DB Info
	db = mysql.connector.connect(
		host=mainconfig.dbserver,
		user=mainconfig.dbuser,
		passwd=mainconfig.dbpassword,
		database=mainconfig.sensordb
	)
	# Data Query
	dbcursor = db.cursor()
	if mainconfig.loglevel >= 2:
		codebase.logtime("check")
		logfile.write("Connected to database.\n")

	dbdataquery = "SELECT * FROM " + sys.argv[1] + " ORDER BY ID DESC LIMIT " + str(
		sensorsenabled * mainconfig.checkrange)
	dbcursor.execute(dbdataquery)
	dbdata = []
	for row in dbcursor:
		dbdata.append(float(row[mainconfig.checkdbdatacolumn]))
	actionstate = str((sum(dbdata)) / mainconfig.checkrange)

	dbcursor.close()
	db.close()

	if mainconfig.loglevel >= 2:
		codebase.logtime("check")
		logfile.write("Data from database was collected.\n")
		codebase.logtime("check")
		logfile.write("Database connection was closed.\n")

	# action check
	actionpoint = getattr(mainconfig, action + "activation")

	if mainconfig.loglevel >= 2:
		codebase.logtime("check")
		logfile.write("Current state is: " + actionstate + ".\n")
		codebase.logtime("check")
		logfile.write("Current activationpoint is: " + actionpoint + ".\n")

	if actionstate < actionpoint:
		# action
		scriptstartpath = getattr(pathconfig, action + "actionstartpath")

		if mainconfig.loglevel > 0:
			codebase.logtime("check")
			logfile.write("Action needed - starting script " + scriptstartpath + ".\n")

		os.system("/usr/bin/python3 " + scriptstartpath + " " + actionblocknr)

		if mainconfig.loglevel > 0:
			codebase.sensorlogtime()
			logfile.write("Check was processed.\n")

	else:
		if mainconfig.loglevel > 0:
			codebase.logtime("check")
			logfile.write("No action needed.\n")



if sensorsenabled > 0:
	with open(pathconfig.config + "mainconfig.py", 'r') as mainconfigfile:
		whilecount = mainconfigfile.read().count("actionblock")
	while whilecount > 0:
		#check if sensor is in the current actionblock
		actionblock = getattr(mainconfig, "actionblock{:02d}".format(whilecount))
		actionblocknr = "actionblock{:02d}".format(whilecount)
		whilecount -= 1
		#print(whilecount + " " + actionblock)
		sensorcount = str(actionblock).count(sys.argv[1])-1
		if sensorcount > 0:
			#check if action is required
			#check which actions are linked to the current sensor
			actiontypes = mainconfig.actiontypes.get(sys.argv[1])
			actiontypecount = len(actiontypes.split())
			if actiontypecount > 1:
				for action in actiontypes:
					sensoractioncount = str(actionblock).count(action)
					#check if actions are in the current actionblock
					if sensoractioncount > 0:
						actioncheck(action, actionblocknr)
					else:
						print("action " + action + " isn't in the current actionblock")
			else:
				sensoractioncount = str(actionblock).count(actiontypes)
				#check if action is in the current actionblock
				if sensoractioncount > 0:
					actioncheck(actiontypes, actionblocknr)
				else:
					print("action " + actiontypes + " isn't in the current actionblock")

		else:
			print("The sensor isn't in the current actionblock")