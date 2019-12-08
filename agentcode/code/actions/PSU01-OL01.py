#!/usr/bin/python3
#Gembird-EG-PMS2-LAN

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
from time import sleep
import os
import socket
import mysql.connector

import inspect
import sys

from GA import MAINconfig
from GA import CODEbase



#Basic Setup
actor = "PSU01-OL01"

##PSU
PSU01ip = MAINconfig.PSU01ip
PSU01port = MAINconfig.PSU01port

##Logs
logfile = CODEbase.ACTIONlogfile
currentscript = currentfile = inspect.getfile(inspect.currentframe())

CODEbase.ACTIONlogtime()
logfile.write("Script " + currentscript + ".\n")

CODEbase.ACTIONlogtime()
logfile.write("Checking if " + sensor + " is online.\n")



#Check if PSU Webserver is online
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PSU01portint = int(PSU01port)
sockresult = sock.connect((PSU01ip, PSU01portint))

if sockresult == None:
	CODEbase.ACTIONlogtime()
	logfile.write("PSU webserver " + PSU01ip + " is listening on port " + PSU01port + ".\n")
	#Python could stop and throw 'no route to host' error if psu isn't online.
else:
	CODEbase.ACTIONlogtime()
	logfile.write("PSU webserver " + PSU01ip + " port " + PSU01port + " seems to be closed.\n")

sock.close()



#Web Setup
display = Display(visible=0, size=(800, 600))
display.start()

profile = webdriver.FirefoxProfile()
profile.native_events_enabled = False
driver = webdriver.Firefox(profile)
driver.set_page_load_timeout(60)

driver.get("http://" + PSU01ip + ":" + PSU01port)



#Login
driver.find_element_by_name("pw").send_keys(MAINconfig.PSU01password, Keys.ENTER)

CODEbase.ACTIONlogtime()
logfile.write("Login Done.\n")

sleep(3)



#Outlet-Status-Change
outlet01 = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/table[1]/tbody/tr[2]/td[1]/span/a")
outletstatus01 = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/table[1]/tbody/tr[2]/td[1]/span/span")
outletstatus02 = outletstatus01.get_attribute("innerHTML")

CODEbase.ACTIONlogtime()
logfile.write(sensor + " Status is " + outletstatus02 + ".\n")

outlet01.click()
sleep(3)

outletstatus03 = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/table[1]/tbody/tr[2]/td[1]/span/span")
outletstatus04 = outletstatus03.get_attribute("innerHTML")

CODEbase.ACTIONlogtime()
logfile.write(sensor + " Status was changed to " + outletstatus04 + ".\n")
sleep(3)



#Logout (if not -> impossible to log back in)
driver.find_element_by_xpath("/html/body/div/div/div[1]/div[2]/div[9]/a").click()

CODEbase.ACTIONlogtime()
logfile.write("Logout Done.\n")

sleep(3)



#Web CleanUp
driver.quit()

sleep(10)

os.system("pkill firefox*")
os.system("rm -rf /tmp/tmp*")

CODEbase.ACTIONlogtime()
logfile.write("All Firefox processes killed and their profiles (/tmp/tmp*) were purged.\n")



#Log to Database
ACTIONtaken = "State was changed from " + outletstatus02 + " to " + outletstatus04 

GAdb = mysql.connector.connect(
  host=MAINconfig.DATABASEserver,
  user=MAINconfig.DATABASEuser,
  passwd=MAINconfig.DATABASEpassword,
  database=MAINconfig.ACTIONdatabase
)
GAdbcursor = GAdb.cursor()

CODEbase.ACTIONlogtime()
logfile.write("Connected to database " + MAINconfig.ACTIONdatabase + ".\n")

sql = "INSERT INTO PSU (DATE, TIME, CONTROLLER, ACTOR, ACTIONTAKEN, OLUSAGE) VALUES (%s, %s, %s, %s, %s, %s)"
val = (CODEbase.date01, CODEbase.time02, MAINconfig.controller, actor, ACTIONtaken, MAINconfig.PSU01OL01usage)
GAdbcursor.execute(sql, val)
GAdb.commit()

CODEbase.ACTIONlogtime()
logfile.write(str(GAdbcursor.rowcount) +  " line was inserted into the Database " + MAINconfig.ACTIONdatabase + ".\n")
CODEbase.ACTIONlogtime()
logfile.write("Row-ID:" + str(GAdbcursor.lastrowid) + ".\n")

GAdbcursor.close()
GAdb.close()

CODEbase.ACTIONlogtime()
logfile.write("Database connection was closed.\n")
