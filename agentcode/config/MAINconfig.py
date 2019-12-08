#!/usr/bin/python3

#General Growautomation Configuration
##### FORMAT is case-sensitive!!! #####
controller = "CON01"

DATABASEserver = "IP"
DATABASEuser = "GA-0101-CON01"
DATABASEpassword = "PASSWORD"
SENSORdatabase = "GA0101SENSORS"
ACTIONdatabase = "GA0101ACTIONS"


#Backup
BACKUPenabled = "YES" #YES/NO -> If Backup should be created
BACKUPtime = "20:00"

#Logs
LOGlevel = 2	#2=debug/1=default/0=none
LOGbackup = "YES"   #YES/NO -> If Logs should be included into the backup


#Sensors

#General Settings
SENSORtime = "10"		        #Every ? minutes the sensordata will be written to the database
SENSORahtdisabled = "NO"
SENSORehdisabled = "NO"


#Air Humidity Temperature
#AHTA = Adafruit DHT22
AHTdisabled = ["AHTA02"]

AHTAconnected = ["AHTA01"]
AHTApins = ["26", "19"]

#Earth Humidity
#EHA = generic analog china humidity sensor
#EHB = analog capacitive soil moisture sensor v1.2 (find on amazon)

EHAdisabled = ["EHA02", "EHA03"]
EHBdisabled = ["EHB02"]

EHAconnected = ["EHA01", "EHA02", "EHA03"]
EHBconnected = ["EHB01", "EHB02"]



#Acions
#EH
PUMPactivation = "60"		#The pump will be activated if the humidity falls under this value
PUMPtime = "600"		#Runtime in seconds

#Window-Openers
WINconnected = ["WIN01", "WIN02"]
WINopentime = 5
WINpinfwd = ["20", "16"]
WINpinrev = ["21", "12"]

#Power Strips
#PSU01 = Gembird Energenie EG-PMS2-LAN
#PSU02 =
##PSU01
PSU01password = "PASSWORD"
PSU01ip = "IP"
PSU01port = "PORT"

###Outlet 1
PSU01OL01usage = "None"

###Outlet 2
PSU01OL02usage = "None"

###Outlet 3
PSU01OL03usage = "None"

###Outlet 4
PSU01OL04usage = "None"
