#!/usr/bin/python3

#import mysql.connector
#from time import sleep
#import os
import inspect
import sys

from GA import MAINconfig
from GA import PATHconfig
#from GA import CODEbase


# Logs
#logfile = CODEbase.CHECKlogfile
#if MAINconfig.LOGlevel > 0:
currentscript = currentfile = inspect.getfile(inspect.currentframe())
#    CODEbase.CHECKlogtime()
#    logfile.write("Script " + currentscript + ".\n")

#if MAINconfig.LOGlevel >= 2:
#    CODEbase.CHECKlogtime()
#    logfile.write("Connecting to database " + MAINconfig.SENSORdatabase + ".\n")


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


if SENSORSenabled > 0:
	#with open(PATHconfig.root + "config/MAINconfig.py", 'r') as MAINconfigfile:
	with open("C:/Users/Administrator/git/controller/agentcode/config/MAINconfig.py", 'r') as MAINconfigfile:
		whilecount = MAINconfigfile.read().count("ACTIONblock")
	while whilecount > 0:
		#Check if sensor is in the current actionblock
		ACTIONblock = getattr(MAINconfig, "ACTIONblock{:02d}".format(whilecount))
		whilecount -= 1
		#print(whilecount + " " + ACTIONblock)
		SENSORcount = str(ACTIONblock).count(sys.argv[1])-1
		if SENSORcount > 0:
			#Check which actions are linked to the current sensor
			ACTIONtypes = MAINconfig.ACTIONtypes.get(sys.argv[1])
			ACTIONtypecount = len(ACTIONtypes.split())
			if ACTIONtypecount > 1:
				for action in ACTIONtypes:
					SENSORactioncount = str(ACTIONblock).count(action)
					#Check if actions are in the current actionblock
					if SENSORactioncount > 0:
						print("DO multiple " + action + " ACTION NAUW")
					else:
						print("Action " + action + " isn't in the current actionblock")
			else:
				SENSORactioncount = str(ACTIONblock).count(ACTIONtypes)
				#Check if action is in the current actionblock
				if SENSORactioncount > 0:
					print("DO one " + ACTIONtypes + " ACTION NAUW")
				else:
					print("Action " + ACTIONtypes + " isn't in the current actionblock")

		else:
			print("The sensor isn't in the current actionblock")