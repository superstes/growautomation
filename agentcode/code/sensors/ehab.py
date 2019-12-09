#!/usr/bin/python3

import inspect
import mysql.connector
import Adafruit_ADS1x15

from GA import mainconfig
from GA import codebase


#log Setup
logfile = codebase.logopen("sensor")
if mainconfig.loglevel > 0:
        currentscript = currentfile = inspect.getfile(inspect.currentframe())
        codebase.logtime("sensor")
        logfile.write("Script " + currentscript + ".\n")

for sensor, adc in mainconfig.ehabconnected.items():
        for adctmp in adc:
            adcnr = adctmp
            adcpin = adc[adctmp]

        if sensor in mainconfig.ehabdisabled:
            if mainconfig.loglevel > 0:
                codebase.logtime("sensor")
                logfile.write("Sensor " + sensor + " on adc " + adc + " was disabled.\n")
            #print(sensor + " on adc " + adcnr + " is disabled")
        elif adcnr in mainconfig.adcdisabled:
            if mainconfig.loglevel > 0:
                codebase.logtime("sensor")
                logfile.write("adc " + adc + " was disabled.\n")
            #print("adc " + adcnr + " for sensor " + sensor + " is disabled")
        else:
            if mainconfig.loglevel >= 2:
                codebase.logtime("sensor")
                logfile.write("Processing sensor: " + sensor + "\n")
                logfile.write("Sensor is connected to " + adcpin + " on adc " + adcnr + "\n")
            #print(sensor + " on adc " + adcnr + " is enabled")

            datahumi = Adafruit_ADS1x15.ADS1115().read_adc(adcpin)

            if mainconfig.loglevel >= 2:
                codebase.logtime("sensor")
                logfile.write("Sensor data received. Connecting to database " + mainconfig.sensordb + ".\n")

            db = mysql.connector.connect(
                host=mainconfig.dbserver,
                user=mainconfig.dbuser,
                passwd=mainconfig.dbpassword,
                database=mainconfig.sensordb
            )
            dbcursor = db.cursor()

            if mainconfig.loglevel >= 2:
                codebase.logtime("sensor")
                logfile.write("Connected to database.\n")

            # DB Data Insert
            sql = "INSERT INTO eh (DATE, TIME, CONTROLLER, SENSOR, HUMIDITY) VALUES (%s, %s, %s, %s, %s)"
            val = (codebase.date01, codebase.time02, mainconfig.controller, sensor, datahumi)
            dbcursor.execute(sql, val)
            db.commit()

            if mainconfig.loglevel >= 2:
                codebase.logtime("sensor")
                logfile.write(str(dbcursor.rowcount) + " line was inserted into the Database " + mainconfig.sensordb + ".\n")
                codebase.logtime("sensor")
                logfile.write("Row-ID:" + str(dbcursor.lastrowid) + ".\n")

            # DB Close
            dbcursor.close()
            db.close()

            if mainconfig.loglevel >= 2:
                codebase.logtime("sensor")
                logfile.write("Database connection was closed.\n")

            if mainconfig.loglevel > 0:
                codebase.logtime("sensor")
                logfile.write("Sensor was processed: " + sensor + "\n")