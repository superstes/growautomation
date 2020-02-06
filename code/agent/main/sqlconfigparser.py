#!/usr/bin/python3
#ga_version0.2.1.2
import mysql.connector

def actioncheck(actionblockcurrent, actionsinblock):
	db = mysql.connector.connect(
		host=mainconfig.dbserver,
		user=mainconfig.dbuser,
		passwd=mainconfig.dbpassword,
		database=mainconfig.sensordb
	)