#!/usr/bin/python3

import inspect
import mysql.connector
import Adafruit_ADS1x15

from GA import MAINconfig
from GA import CODEbase


#Log Setup
logfile = CODEbase.SENSORlogfile
if MAINconfig.LOGlevel > 0:
        currentscript = currentfile = inspect.getfile(inspect.currentframe())
        CODEbase.SENSORlogtime()
        logfile.write("Script " + currentscript + ".\n")

#print(MAINconfig.EHABconnected)

for sensor, adc in MAINconfig.EHABconnected.items():
        for adctmp in adc:
            adcnr = adctmp
            adcpin = adc[adctmp]

        if sensor in MAINconfig.EHABdisabled:
            if MAINconfig.LOGlevel > 0:
                CODEbase.SENSORlogtime()
                logfile.write("Sensor " + sensor + " on ADC " + adc + " was disabled.\n")
            #print(sensor + " on ADC " + adcnr + " is disabled")
        elif adcnr in MAINconfig.ADCdisabled:
            if MAINconfig.LOGlevel > 0:
                CODEbase.SENSORlogtime()
                logfile.write("ADC " + adc + " was disabled.\n")
            #print("ADC " + adcnr + " for sensor " + sensor + " is disabled")
        else:
            if MAINconfig.LOGlevel >= 2:
                CODEbase.SENSORlogtime()
                logfile.write("Processing sensor: " + sensor + "\n")
                logfile.write("Sensor is connected to " + adcpin + " on ADC " + adcnr + "\n")
            #print(sensor + " on ADC " + adcnr + " is enabled")

            datahumi = Adafruit_ADS1x15.ADS1115().read_adc(adcpin)

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
            sql = "INSERT INTO EH (DATE, TIME, CONTROLLER, SENSOR, HUMIDITY) VALUES (%s, %s, %s, %s, %s)"
            val = (CODEbase.date01, CODEbase.time02, MAINconfig.controller, sensor, datahumi)
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