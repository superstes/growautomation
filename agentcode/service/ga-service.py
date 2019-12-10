#!/usr/bin/python3
import schedule
import time
import os
from importlib import reload
import sys

import GA.PATHconfig
import GA.MAINconfig


#Timers

#Backup timer
def backup():
    os.system("/usr/bin/python3 " + GA.PATHconfig.root + "code/backup/backup.py")

schedule.every().day.at(GA.MAINconfig.BACKUPtime).do(backup)

#Sensor timer
def sensor():
    os.system("/usr/bin/python3 " + GA.PATHconfig.root + "code/sensors/sensor.py")

schedule.every(GA.MAINconfig.SENSORtime).minutes.do(sensor)

#Check timer
def check():
    os.system("/usr/bin/python3 " + GA.PATHconfig.root + "code/checks/check.py")

schedule.every(GA.MAINconfig.CHECKtime).minutes.do(check)




if "__main__" == __name__:
    if "reload" in sys.argv:
        reload(GA.PATHconfig)
        reload(GA.MAINconfig)
        sys.exit("Service configuration was reloaded.")

while True:
    schedule.run_pending()
    time.sleep(1)

