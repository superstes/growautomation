#!/usr/bin/python3

import inspect
import mysql.connector
import Adafruit_DHT

from GA import mainconfig
from GA import codebase


#log Setup
logfile = codebase.logopen("sensor")
if mainconfig.loglevel > 0:
        currentscript = currentfile = inspect.getfile(inspect.currentframe())
        codebase.logtime("sensor")
        logfile.write("Script " + currentscript + ".\n")

for sensor, pin in mainconfig.ahtaconnected.items():
        if sensor in mainconfig.ahtadisabled:
            if mainconfig.loglevel > 0:
                   codebase.logtime("sensor")
                   logfile.write("Sensor " + sensor + " was disabled.\n")
            # print(sensor + " on pin " + pin + " is disabled")
        else:
            if mainconfig.loglevel >= 2:
                codebase.logtime("sensor")
                logfile.write("\nProcessing sensor: " + sensor + "\n")
            # print(sensor + " on pin " + pin + " is enabled")

            datahumi, datatemp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, pin)

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
            sql = "INSERT INTO aht (DATE, TIME, CONTROLLER, SENSOR, TEMPERATURE, HUMIDITY) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (codebase.date01, codebase.time02, mainconfig.controller, sensor, datatemp, datahumi)
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