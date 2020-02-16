#!/usr/bin/python
# This file is part of Growautomation
#     Copyright (C) 2020  René Pascal Rath
#
#     Growautomation is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#     E-Mail: rene.rath@growautomation.at
#     Web: https://git.growautomation.at

import os
import mysql.connector
import inspect
import sys


#PSU web interface interactions
from selenium import webdriver as seleniumwebdriver
from selenium.webdriver.common.keys import Keys as seleniumkeys
from pyvirtualdisplay import Display as pyvirtualdisplaydriver
import socket
from time import sleep


from GA import mainconfig
from GA import codebase
from GA import pathconfig

#sys.argv[1] = actionblock (pe actionblock01)
#sys.argv[2] = actiontype (pe pump)

# Functionality
# Gets executed from check.py - it passes the actionblock and actiontype
# 1. Check objects      lists all actionobjects in the actionblock which should be processed
# 2. Check outlets      links the actionobjects and their psu outlets for further processing
# 3. Action             changes powerstate for every actionobject found in 1.
#                       uses the information from 2. to know which outletstatus should be changed
# 4. Action timer       times the action like configured (on/off seconds)

# Logs

if mainconfig.loglevel > 0:
    logfile = codebase.logopen("action")
    currentscript = currentfile = inspect.getfile(inspect.currentframe())
    codebase.logtime("action")
    logfile.write("Script " + currentscript + ".\n")

# System arguments
actionblocknr = sys.argv[1]
#actionblocknr = codebase.actionblocksysargcheck(sys.argv)
actiontype = sys.argv[2]

# Check objects

actionblock = getattr(mainconfig, actionblocknr)
actionobjectlist = []
for key, actionobject in actionblock.items():
    if "actions" in key:
        for subkey, actionsubobject in actionobject.items():
            for item in actionsubobject:
                if item.find(actiontype) >= 0:
                    actionobjectlist.append(item)
#print(actionobjectlist)

# Check outlets
psulist = codebase.namegen("psu")
actioninfo = {}
for psu in psulist:
    psuoutlet = psu + "outlets"
    with open(pathconfig.config + "mainconfig.py", 'r') as mainconfigfile:
        outletcount = mainconfigfile.read().count(psuoutlet)
        if outletcount > 0:
            outletinfo = getattr(mainconfig, psuoutlet)
            objectcount = 1
            for obj in actionobjectlist:
                objectcount += 1
                for outlet, outletuse in outletinfo.items():
                    if obj in outletuse:
                        actioninfo.update({obj: {psu: outlet}})
#print(actioninfo)

# Action
# Note: will be optimized in future (first loop per psu than loop per outlet for better performance)
def psuaction(obj, val):
    for psu, outlet in val.items():
        psuip = getattr(mainconfig, psu + "ip")
        psuwebport = getattr(mainconfig, psu + "webport")
        psupassword = getattr(mainconfig, psu + "password")

        if mainconfig.loglevel >= 2:
            codebase.logtime("action")
            logfile.write("Checking if " + psu + " is online.\n")

        # Check if PSU webserver is online
        websock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        websockresult = websock.connect(psuip, psuwebport)

        if websockresult is None:
            if mainconfig.loglevel >= 2:
                codebase.logtime("action")
                logfile.write("PSU webserver " + psuip + " is listening on port " + psuwebport + ".\n")

        else:
            if mainconfig.loglevel >= 2:
                codebase.logtime("action")
                logfile.write("PSU webserver " + psuip + " port " + psuwebport + " seems to be closed.\n")

            raise SystemExit("\nPSU webserver not reachable.")

        websock.close()

        # Use webdriver to log into the psu webinterface and change the outlet status
        pyvirtualdisplaydriver(visible=0, size=(800, 600)).start()

        profile = seleniumwebdriver.FirefoxProfile()
        profile.native_events_enabled = False
        driver = seleniumwebdriver.Firefox(profile)
        driver.set_page_load_timeout(60)

        driver.get("http://" + psuip + ":" + psuwebport)

        # Login
        driver.find_element_by_name("pw").send_keys(psupassword, seleniumkeys.ENTER)

        if mainconfig.loglevel >= 2:
            codebase.logtime("action")
            logfile.write("Login done.\n")

        sleep(3)

        # Change outlet status
        outletbutton = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/table[1]/tbody/tr[2]/td[" + outlet + "]/span/a")
        outletbuttonelement = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/table[1]/tbody/tr[2]/td[1]/span/span")
        outletstatusbefore = outletbuttonelement.get_attribute("innerHTML")

        if mainconfig.loglevel >= 2:
            codebase.logtime("action")
            logfile.write(obj + " status is " + outletstatusbefore + ".\n")

        outletbutton.click()
        sleep(3)

        outletstatusafter = outletbuttonelement.get_attribute("innerHTML")

        if mainconfig.loglevel >= 2:
            codebase.logtime("action")
            logfile.write(obj + " status was changed to " + outletstatusafter + ".\n")

        sleep(3)

        # Logout (if not -> impossible to log back in)
        driver.find_element_by_xpath("/html/body/div/div/div[1]/div[2]/div[9]/a").click()

        if mainconfig.loglevel >= 2:
            codebase.logtime("action")
            logfile.write("Logout Done.\n")

        sleep(3)

        # Web cleanup
        driver.quit()

        sleep(10)

        os.system("pkill firefox*")
        os.system("rm -rf /tmp/tmp*")

        if mainconfig.loglevel >= 2:
            codebase.logtime("action")
            logfile.write("All Firefox processes killed and their profiles (/tmp/tmp*) were purged.\n")

        if mainconfig.logactiontodb == "yes":
            # Log to Database

            db = mysql.connector.connect(
                host=mainconfig.dbserver,
                user=mainconfig.dbuser,
                passwd=mainconfig.dbpassword,
                database=mainconfig.actiondb
            )

            actiontaken = outletstatusbefore + " to " + outletstatusafter

            dbcursor = db.cursor()

            if mainconfig.loglevel >= 2:
                codebase.logtime("action")
                logfile.write("Connected to database " + mainconfig.actiondb + ".\n")

            sql = "INSERT INTO PSU (DATE, TIME, CONTROLLER, ACTOR, ACTIONTAKEN, OLUSAGE) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (codebase.date01, codebase.time02, mainconfig.controller, psu, actiontaken, obj)
            dbcursor.execute(sql, val)
            db.commit()

            if mainconfig.loglevel >= 2:
                codebase.logtime("action")
                logfile.write(str(dbcursor.rowcount) + " line was inserted into the Database " + mainconfig.actiondb + ".\n")
                codebase.logtime("action")
                logfile.write("Row-ID:" + str(dbcursor.lastrowid) + ".\n")

            dbcursor.close()
            db.close()

            if mainconfig.loglevel >= 2:
                codebase.logtime("action")
                logfile.write("Database connection was closed.\n")

# Action timer
for obj, val in actioninfo.items():
    for action in mainconfig.actiontypes.values():
        if action in actiontype:
            psusleep = getattr(mainconfig, action + "time")
            if psusleep > 0:
                psuaction(obj, val)
                sleep(psusleep)
                psuaction(obj, val)
            else:
                if mainconfig.loglevel > 0:
                    codebase.logtime("action")
                    logfile.write("Configuration error. " + action + "time: No time provided or wrong format.\n")

                raise SystemExit("\nConfiguration error. Var " + action + "time: no time provided or wrong format.\nData: " + str(psusleep) + "\n")