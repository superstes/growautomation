#!/usr/bin/python3

import inspect
import mysql.connector
import Adafruit_DHT

from GA import MAINconfig
from GA import CODEbase


#Log Setup
logfile = CODEbase.SENSORlogfile
if MAINconfig.LOGlevel > 0:
        currentscript = currentfile = inspect.getfile(inspect.currentframe())
        CODEbase.SENSORlogtime()
        logfile.write("Script " + currentscript + ".\n")

#print(MAINconfig.AHTAconnected)

for sensor, pin in MAINconfig.AHTAconnected.items():
        if sensor in MAINconfig.AHTAdisabled:
            if MAINconfig.LOGlevel > 0:
                   CODEbase.SENSORlogtime()
                   logfile.write("Sensor " + sensor + " was disabled.\n")
            # print(sensor + " on pin " + pin + " is disabled")
        else:
            if MAINconfig.LOGlevel >= 2:
                CODEbase.SENSORlogtime()
                logfile.write("\nProcessing sensor: " + sensor + "\n")
            # print(sensor + " on pin " + pin + " is enabled")

            datahumi, datatemp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, pin)

            if MAINconfig.LOGlevel >= 2:
                CODEbase.SENSORlogtime()
                logfile.write("Sensor data received. Connecting to database " + MAINconfig.SENSORdatabase + ".\n")

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

            # DB Data Insert
            sql = "INSERT INTO AHT (DATE, TIME, CONTROLLER, SENSOR, TEMPERATURE, HUMIDITY) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (CODEbase.date01, CODEbase.time02, MAINconfig.controller, sensor, datatemp, datahumi)
            GAdbcursor.execute(sql, val)
            GAdb.commit()

            if MAINconfig.LOGlevel >= 2:
                CODEbase.SENSORlogtime()
                logfile.write(str(GAdbcursor.rowcount) + " line was inserted into the Database " + MAINconfig.SENSORdatabase + ".\n")
                CODEbase.SENSORlogtime()
                logfile.write("Row-ID:" + str(GAdbcursor.lastrowid) + ".\n")

            # DB Close
            GAdbcursor.close()
            GAdb.close()

            if MAINconfig.LOGlevel >= 2:
                CODEbase.SENSORlogtime()
                logfile.write("Database connection was closed.\n")

            if MAINconfig.LOGlevel > 0:
                CODEbase.SENSORlogtime()
                logfile.write("Sensor was processed: " + sensor + "\n")