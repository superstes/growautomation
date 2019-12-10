#!/usr/bin/python3

#Growautomation File-Path Configuration

#General
root = "/etc/growautomation/"
logs = "/var/log/growautomation/"
backup = "/mnt/growautomation/backup/"

code = root + "code/"
config = root + "config/"

#Sensors
sensors = code + "sensors/"

#Acions
actions = code + "actions/"
pumpaaction = actions + "psua.py"
winaaction = actions + "wina.py"

#Checks
checks = code + "checks/"
