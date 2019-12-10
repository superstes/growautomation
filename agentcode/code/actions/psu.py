#!/usr/bin/python3

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

# Logs
logfile = codebase.logopen("action")
if mainconfig.loglevel > 0:
    currentscript = currentfile = inspect.getfile(inspect.currentframe())
    codebase.logtime("action")
    logfile.write("Script " + currentscript + ".\n")

# System arguments
actionblocknr = sys.argv[1]
#actionblocknr = codebase.actionblocksysargcheck(sys.argv)
actiontype = sys.argv[2]

# Check actionobjects

actionblock = getattr(mainconfig, actionblocknr)
actionobjectlist = []
for key, actionobject in actionblock.items():
# Splitting actionblock into key parts
    if "actions" in key:
    # Getting rid of the sensor key part
        for subkey, actionsubobject in actionobject.items():
        # Splitting the action part into key and value
            for item in actionsubobject:
            # Splitting the nested value into key and value
                if item.find(actiontype) >= 0:
                # Checking if the found actionobject should be processed
                    actionobjectlist.append(item)
                    # Getting a list of the actionobjects in the actionblock which we need to process

# Check which outlets are used for the actionobjects

psulist = codebase.namegen("psu")
# Getting list of possible outlets

actioninfo = {}
for psu in psulist:
    psuoutlet = psu + "outlets"
    with open(pathconfig.config + "mainconfig.py", 'r') as mainconfigfile:
        outletcount = mainconfigfile.read().count(psuoutlet)
        # Checking if a outlet exists in the configuration
        if outletcount > 0:
            outletinfo = getattr(mainconfig, psuoutlet)
            objectcount = 1
            for obj in actionobjectlist:
            # Splitting up actionobjects
                objectcount += 1
                for outlet, outletuse in outletinfo.items():
                # Splitting up outets
                    if obj in outletuse:
                        actioninfo.update({obj: {psu: outlet}})

# Action
# Note: will be optimized in future (first loop per psu than loop per outlet for better performance)
for obj, val in actioninfo.items():
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

            sys.exit("\nPSU webserver not reachable.")

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
