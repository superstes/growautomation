#!/usr/bin/python3
#Growautomation General Configuration File
##### FORMAT is case-sensitive!!! #####

#############################  General  #############################

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
LOGlevel = 0	#2=debug/1=default/0=none
LOGbackup = "YES"   #YES/NO -> If Logs should be included into the backup


#############################  SENSORS  #############################

#General Settings
SENSORtime = "10"		        #How often should the sensordata be written to the database (minutes)
SENSORahtdisabled = "NO"
SENSORehdisabled = "NO"

#Analog to Digital Converters
ADCdisabled = ["ADC02"]

#Which i2c bus the adc is connected to
ADCconnected = {"ADC01": "i2c-1", "ADC02": "i2c-2"}


#Air Humidity Temperature
#AHTA = Adafruit DHT22
AHTAdisabled = ["AHTA02"]

#Format:
#       {
#       "AHTANR": "PIN",
#       "AHTANR": "PIN"
#       }
AHTAconnected = {"AHTA01": "26", "AHTA02": "19"}

#Earth Humidity
#EHA = generic analog china humidity sensor
#EHB = analog capacitive soil moisture sensor v1.2 (find on amazon)

#Format ["EHxNR", "EHxNR"]
EHABdisabled = ["EHB02"]

#Format:
#       {
#       "EHxNR": {
#           "AnalogToDigitalConverterNR": "ADCpinNR"
#           },
#       "EHxNR": {
#           "ADCNR": "ADCpinNR"
#           }
#       }
EHABconnected = {"EHB01": {"ADC01": "0"}, "EHB02": {"ADC02": "1"}}


############################# CHECKS #############################

#How many sensor data records should be checked to determine if an action should be taken
CHECKrange = 6
#row containing the sensor data	-> counted from left without counting the ID row
CHECKdbdatacolumn = 4


#############################  ACTIONS  #############################

#Actiontypes
#Which action should react to which sensortype
ACTIONtypes = {"EH": ("PUMP"), "AHT": ("WIN")}


#Actionblocks
#Links sensors and actions -> simplifies configuration and processing
#Use '*' as wildcard if all enabled sensors in the category should be used
#Format:
#       {
#       "SENSORS": {
#           "EH": ("*"),
#           "AHT": ("*")
#           },
#       "ACTIONS": {
#           "PUMP": ("*"),
#           "WIN": ("*")
#           }
#       }
ACTIONblock01 = {"SENSORS": {"EH": ("EHB01", "EHB02"), "AHT": ("AHT01", "AHT02")}, "ACTIONS": {"WIN": ("*")}}
ACTIONblock02 = {"SENSORS": {"EH": ("EHB01", "EHB02")}, "ACTIONS": {"PUMP": ("PUMP01")}}


#Water Pumps
#Generic water pumps -> are controlled via network attached power strip
PUMPdisabled = []

#Format:
#       {
#       "PUMPNR": {
#           "PowerStripNR": "PSUsocketNR"
#           },
#       "PUMPNR": {
#           "PSUNR": "PSUsocketNR"
#           }
#       }
PUMPconnected = {"PUMP01": {"PSU01": "1"}}

PUMPactivation = "60"		#The pump will be activated if the humidity falls under this value
PUMPtime = 600		#Runtime in seconds

#Window-Openers
#12V DC motors with 3d-printed window-opener attachments
#DC motor driver L298N Dual-H-Bridge
WINdisabled = {}

#Format:
#       {
#       "WINNR": {
#           "FWD": "PINForward",
#           "REV": "PINReverse"
#           },
#       "WINNR": {
#           "FWD": "PINForward,
#           "REV": "PINReverse"
#           }
#       }
WINconnected = {"WIN01": {"FWD": "20", "REV": "21"}, "WIN02": {"FWD": "16", "REV": "12"}}
WINopentime = 5

#Power Strips
#PSUA: Gembird Energenie EG-PMS2-LAN (trashy hard- and firmware) -> would not recommend buying it
#PSUB: Coming soon (:
PSUA01password = "PASSWORD"
PSUA01ip = "IP"
PSUA01port = "PORT"
