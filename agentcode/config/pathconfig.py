#!/usr/bin/python3

#Growautomation File-Path Configuration

#General
#root = "/etc/growautomation/"
root = "C:/users/Administrator/git/controller/agentcode/"
#logs = "/var/log/growautomation/"
logs = "C:/users/Administrator/git/logs/"
#backup = "/mnt/growautomation/backup/"
backup = "C:/users/Administrator/git/backup/"
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
