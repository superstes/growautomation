#!/usr/bin/python3
#Growautomation General Configuration File
##### FORMAT is case-sensitive!!! #####

#############################  General  #############################

controller = "con01"

dbserver = "IP"
dbuser = "con01"
dbpassword = "PASSWORD"
sensordb = "sensors"
actiondb = "actions"


#backup
backupenabled = "yes" #yes/no -> If backup should be created
backuptime = "20:00"

#logs
loglevel = 0	#2=debug/1=default/0=none
logbackup = "yes"   #yes/no -> If logs should be included into the backup
logactiontodb = "yes" #yes/no -> If taken actions should be logged into the database


#############################  sensorS  #############################

#General Settings
sensortime = "10"		        #How often should the sensordata be written to the database (minutes)
sensorahtdisabled = "no"
sensorehdisabled = "no"

#Analog to Digital Converters
adcdisabled = ["adc02"]

#Which i2c bus the adc is connected to
adcconnected = {"adc01": "i2c-1", "adc02": "i2c-2"}


#Air Humidity Temperature
#ahta = Adafruit DHT22
ahtadisabled = ["ahta02"]

#Format:
#       {
#       "ahtaNR": "PIN",
#       "ahtaNR": "PIN"
#       }
ahtaconnected = {"ahta01": "26", "ahta02": "19"}

#Earth Humidity
#eha = generic analog china humidity sensor
#ehb = analog capacitive soil moisture sensor v1.2 (find on amazon)

#Format ["ehxNR", "ehxNR"]
ehabdisabled = ["ehb02"]

#Format:
#       {
#       "ehxNR": {
#           "AnalogToDigitalConverterNR": "adcpinNR"
#           },
#       "ehxNR": {
#           "adcNR": "adcpinNR"
#           }
#       }
ehabconnected = {"ehb01": {"adc01": "0"}, "ehb02": {"adc02": "1"}}


############################# CHECKS #############################

#How many sensor data records should be checked to determine if an action should be taken
CHECKrange = 6
#row containing the sensor data	-> counted from left without counting the ID row
CHECKdbdatacolumn = 4


#############################  actions  #############################

#actiontypes
#Which action should react to which sensortype
actiontypes = {"eh": ("pump"), "aht": ("win")}


#actionblocks
#Links sensors and actions -> simplifies configuration and processing
#Use '*' as wildcard if all enabled sensors in the category should be used
#Format:
#       {
#       "sensorS": {
#           "eh": ("*"),
#           "aht": ("*")
#           },
#       "actions": {
#           "pump": ("*"),
#           "win": ("*")
#           }
#       }
actionblock01 = {"sensorS": {"eh": ("ehb01", "ehb02"), "aht": ("aht01", "aht02")}, "actions": {"win": ("*")}}
actionblock02 = {"sensorS": {"eh": ("ehb01", "ehb02")}, "actions": {"pump": ("pump01")}}


#Water pumps
#Generic water pumps -> are controlled via network attached power strip
pumpdisabled = []

#Format:
#       {
#       "pumpNR": {
#           "PowerStripNR": "psusocketNR"
#           },
#       "pumpNR": {
#           "psuNR": "psusocketNR"
#           }
#       }
pumpconnected = {"pump01": {"psu01": "1"}}

pumpactivation = "60"		#The pump will be activated if the humidity falls under this value
pumptime = 600		#Runtime in seconds

#window-Openers
#12V DC motors with 3d-printed window-opener attachments
#DC motor driver L298N Dual-H-Bridge
windisabled = {}

#Format:
#       {
#       "winNR": {
#           "FWD": "PINForward",
#           "REV": "PINReverse"
#           },
#       "winNR": {
#           "FWD": "PINForward,
#           "REV": "PINReverse"
#           }
#       }
winconnected = {"win01": {"FWD": "20", "REV": "21"}, "win02": {"FWD": "16", "REV": "12"}}
winopentime = 5

#Power Strips
#psua: Gembird Energenie EG-PMS2-LAN (trashy hard- and firmware) -> would not recommend buying it
#psub: Coming soon (:
psua01password = "PASSWORD"
psua01ip = "IP"
psua01port = "PORT"
