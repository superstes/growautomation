#!/usr/bin/python3

import mysql.connector
import os
import inspect
import sys

from GA import mainconfig
from GA import pathconfig
from GA import codebase

#sys.argv[1] = sensortype (pe eh)

# Functionality
# Gets executed from growautomation service/timer - it passes the sensortype
# 1. Check function     pulls threshold data for the current sensor from the database
#						it executes the decision function for every actionobject linked to the current sensor
# 2. Decision function	compares actionpoint and -state and decides if the action should be started
# 3. Action function	executes the action for every actionobject in the current actionblock
# 4. Precheck		    checks configuration for actiontype-links and actionobjects linked to the current sensor
#						if no errors found -> it executes the check function

# Logs
if mainconfig.loglevel > 0:
	logfile = codebase.logopen("check")
	currentscript = currentfile = inspect.getfile(inspect.currentframe())
	codebase.logtime("check")
	logfile.write("Script " + currentscript + ".\n")

# System arguments
sensortype = sys.argv[1]

# Sensors enabled
sensorsenabled = codebase.sensorenabledcheck(sensortype)

# Check function
def actioncheck(actionblockcurrent, actionsinblock):
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

	def actiondecision(action, actionstate):
		# Action check
		actionpoint = getattr(mainconfig, action + "activation")

		if mainconfig.loglevel >= 2:
			codebase.logtime("check")
			logfile.write("Current state is: " + actionstate + ".\n")
			codebase.logtime("check")
			logfile.write("Current activationpoint is: " + actionpoint + ".\n")

		if int(actionstate) > actionpoint:
			return True
		else:
			return False

	def actionstart(action):
		# Action
		scriptpath = getattr(pathconfig, action + "action")

		if mainconfig.loglevel >= 2:
			codebase.logtime("check")
			logfile.write(
				"Action needed - starting script " + scriptpath + " for actionblock " + actionblockcurrent + ".\n")
		elif mainconfig.loglevel > 0:
			codebase.logtime("check")
			logfile.write("Action needed - starting script " + scriptpath + ".\n")

		# execute script from mainconfig and pass actionblock and actiontype
		os.system("/usr/bin/python3 " + scriptpath + " " + actionblockcurrent + " " + action)

		if mainconfig.loglevel > 0:
			codebase.logtime("check")
			logfile.write("Check was processed.\n")

	try:
		tmp = len(actionsinblock.split())
		if mainconfig.loglevel >= 2:
			codebase.logtime("check")
			logfile.write("Processing " + actionsinblock + ".\n")
		if actiondecision(actionsinblock, actionstate) == True:
			actionstart(actionsinblock)
		elif mainconfig.loglevel >= 2:
				codebase.logtime("check")
				logfile.write("No action needed.\n")

	except AttributeError:
		for action in actionsinblock:
			if mainconfig.loglevel >= 2:
				codebase.logtime("check")
				logfile.write("Processing " + action + ".\n")
			if actiondecision(action, actionstate) == True:
				actionstart(action)
			elif mainconfig.loglevel >= 2:
				codebase.logtime("check")
				logfile.write("No action needed.\n")

# Precheck
if sensorsenabled > 0:
	actiontypes = mainconfig.actiontypes.get(sensortype)
	try:
		actiontypecount = len(actiontypes.split())
	except AttributeError:
		actiontypecount = len(actiontypes)

	if actiontypecount > 0:
		with open(pathconfig.config + "mainconfig.py", 'r') as mainconfigfile:
			actionblockcount = mainconfigfile.read().count("actionblock")
		if actionblockcount	> 0:
			for count in range(actionblockcount):
				actionblockcurrent = "actionblock{:02d}".format(actionblockcount)
				actionblockcount -= 1
				with open(pathconfig.config + "mainconfig.py", 'r') as mainconfigfile:
					actionblockcheck = mainconfigfile.read().count(actionblockcurrent)
				if actionblockcheck > 0:
					actionblock = getattr(mainconfig, actionblockcurrent)
					sensorcount = str(actionblock).count(sensortype)
					if sensorcount > 1:
						actionsinblock = []
						try:
							tmp = len(actiontypes.split())
							actionsinblock.append(actiontypes)
						except AttributeError:
							for action in actiontypes:
								actioncount = str(actionblock).count(action)
								if actioncount > 1:
									actionsinblock.append(action)

						#actioncheck(actionblockcurrent, actionsinblock)
						print(actionblockcurrent, actionsinblock)

					elif mainconfig.loglevel >= 2:
						codebase.logtime("check")
						logfile.write("The sensor " + sensortype + "isn't in the current actionblock " + actionblockcurrent + ".\n")
		else:
			if mainconfig.loglevel > 0:
				codebase.logtime("check")
				logfile.write("No actionblocks could be found in the configuration.\nConfiguration file:\n" + pathconfig.config + "mainconfig.py\n")

			raise SystemExit("\nNo actionblocks could be found in the configuration.")
	else:
		if mainconfig.loglevel >= 2:
			codebase.logtime("check")
			logfile.write("The sensor " + sensortype + " has no actiontypes linked.\nActiontypes:\n" + actiontypes + "\n")

		raise SystemExit("\nThe sensor " + sensortype + " has no actiontypes linked.")
else:
	if mainconfig.loglevel > 0:
		codebase.logtime("check")
		logfile.write("None of the " + sensortype + " sensors are enabled.\nConnected Sensors: " + sensorsconnected + "\nDisabled Sensors: "+ sensorsdisabled + "\n")

	raise SystemExit("\nNone of the " + sensortype + " sensors are enabled.")