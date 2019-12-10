#!/usr/bin/python3

import mysql.connector
import os
import inspect
import sys

from GA import mainconfig
from GA import pathconfig
from GA import codebase



# Logs
logfile = codebase.logopen("check")
if mainconfig.loglevel > 0:
currentscript = currentfile = inspect.getfile(inspect.currentframe())
	codebase.logtime("check")
	logfile.write("Script " + currentscript + ".\n")

# System arguments
if "eh" in sys.argv:
	sensorsconnected = getattr(mainconfig, "ehabconnected")
	sensorsdisabled = getattr(mainconfig, "ehabdisabled")

elif "aht" in sys.argv:
	sensorsconnected = getattr(mainconfig, "ahtaconnected")
	sensorsdisabled = getattr(mainconfig, "ahtadisabled")
else:
	sys.exit("\nInput Error. Sensortype has to be provided as system argument.\n\nExample:\npython3 " + currentscript + " EH")

sensorsenabled = 0
for x in sensorsconnected:
	if x not in sensorsdisabled:
		sensorsenabled += 1
sensortype = sys.argv[1]


# Check function
def actioncheck(actionblocknr, action):
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

	dbdataquery = "SELECT * FROM " + sensortype + " ORDER BY ID DESC LIMIT " + str(sensorsenabled * mainconfig.checkrange)
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

	# Action check
	actionpoint = getattr(mainconfig, action + "activation")

	if mainconfig.loglevel >= 2:
		codebase.logtime("check")
		logfile.write("Current state is: " + actionstate + ".\n")
		codebase.logtime("check")
		logfile.write("Current activationpoint is: " + actionpoint + ".\n")

	if int(actionstate) > actionpoint:
		# Action
		scriptpath = getattr(pathconfig, action + "action")

		if mainconfig.loglevel >= 2:
			codebase.logtime("check")
			logfile.write("Action needed - starting script " + scriptpath + " for actionblock "+ actionblocknr + ".\n")
		elif mainconfig.loglevel > 0:
			codebase.logtime("check")
			logfile.write("Action needed - starting script " + scriptpath + ".\n")

		# execute script from mainconfig and pass actionblock and actiontype
		os.system("/usr/bin/python3 " + scriptpath + " " + actionblocknr + " " + action)

		if mainconfig.loglevel > 0:
			codebase.logtime("check")
			logfile.write("Check was processed.\n")

	else:
		if mainconfig.loglevel > 0:
			codebase.logtime("check")
			logfile.write("No action needed.\n")



if sensorsenabled > 0:
	# check if actioncheck is required
	# check which actions are linked to the current sensor
	actiontypes = mainconfig.actiontypes.get(sensortype)
	actiontypecount = len(actiontypes.split())

	if actiontypecount > 1:

		with open(pathconfig.config + "mainconfig.py", 'r') as mainconfigfile:
			actionblockcount = mainconfigfile.read().count("actionblock")

		if actionblockcount	> 0:

			while actionblockcount > 0:
				#check if sensor is in the current actionblock
				actionblocknr = "actionblock{:02d}".format(actionblockcount)
				actionblock = getattr(mainconfig, actionblocknr)
				sensorcount = str(actionblock).count(sensortype)
				actionblockcount -= 1

				if sensorcount > 1:

					for action in actiontypes:
						# check if there are actions in the current actionblock
						sensoractioncount = str(actionblock).count(action)

						if sensoractioncount > 0:

							if mainconfig.loglevel > 0:
								codebase.logtime("check")
								logfile.write("Starting check for action " + action + " in actionblock " + actionblocknr + ".\n")

							actioncheck(actionblocknr, action)

						elif mainconfig.loglevel >= 2:
							codebase.logtime("check")
							logfile.write("The action " + action + "isn't in the current actionblock " + actionblocknr + ".\n")

				elif mainconfig.loglevel >= 2:
					codebase.logtime("check")
					logfile.write("The sensor " + sensortype + "isn't in the current actionblock " + actionblocknr + ".\n")

		else:
			if mainconfig.loglevel > 0:
				codebase.logtime("check")
				logfile.write("No actionblocks could be found in the configuration.\nConfiguration file:\n" + pathconfig.config + "mainconfig.py\n")

			sys.exit("\nNo actionblocks could be found in the configuration.")

	else:
		if mainconfig.loglevel >= 2:
			codebase.logtime("check")
			logfile.write("The sensor " + sensortype + " has no actiontypes linked.\nActiontypes:\n" + actiontypes + "\n")

		sys.exit("\nThe sensor " + sensortype + " has no actiontypes linked.")

else:
	if mainconfig.loglevel > 0:
		codebase.logtime("check")
		logfile.write("None of the " + sensortype + " sensors are enabled.\nConnected Sensors: " + sensorsconnected + "\nDisabled Sensors: "+ sensorsdisabled + "\n")

	sys.exit("\nNone of the " + sensortype + " sensors are enabled.")