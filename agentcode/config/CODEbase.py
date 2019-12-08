#!/usr/bin/python3

from datetime import datetime
from time import strftime
import os
import inspect
import sys

from GA import PATHconfig


#Time
time01 = datetime.now().strftime("%H-%M-%S")
time02 = datetime.now().strftime("%H:%M:%S")
time03 = datetime.now().strftime("%H-%M")

date01 = datetime.now().strftime("%Y-%m-%d")
date02 = datetime.now().strftime("%Y")
date03 = datetime.now().strftime("%m")
date04 = datetime.now().strftime("%d")


#Logs

##Sensors
if os.path.exists(PATHconfig.SENSORlogs02) is False:
    os.system("mkdir -p " + PATHconfig.SENSORlogs02)

SENSORlogfile = open(PATHconfig.SENSORlogs,'a')

def SENSORlogtime():
    SENSORlogtime01 = datetime.now().strftime("%H:%M:%S:%f")
    SENSORlogfile.write(SENSORlogtime01 + " ")

##Checks
if os.path.exists(PATHconfig.CHECKlogs02) is False:
    os.system("mkdir -p " + PATHconfig.CHECKlogs02)

CHECKlogfile = open(PATHconfig.CHECKlogs,'a')

def CHECKlogtime():
    CHECKlogtime01 = datetime.now().strftime("%H:%M:%S:%f")
    CHECKlogfile.write(CHECKlogtime01 + " ")

##Actions
if os.path.exists(PATHconfig.ACTIONlogs02) is False:
    os.system("mkdir -p " + PATHconfig.ACTIONlogs02)

ACTIONlogfile = open(PATHconfig.ACTIONlogs,'a')

def ACTIONlogtime():
    ACTIONlogtime01 = datetime.now().strftime("%H:%M:%S:%f")
    ACTIONlogfile.write(ACTIONlogtime01 + " ")

##Backups
if os.path.exists(PATHconfig.BACKUPlogs02) is False:
    os.system("mkdir -p " + PATHconfig.BACKUPlogs02)

BACKUPlogfile = open(PATHconfig.BACKUPlogs,'a')

def BACKUPlogtime():
    BACKUPlogtime01 = datetime.now().strftime("%H:%M:%S:%f")
    BACKUPlogfile.write(BACKUPlogtime01 + " ")
