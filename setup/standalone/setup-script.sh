#!/bin/bash
#Notes
#add if elif else for config changes
#also use output.write(input.read(  ).replace(stext, rtext)) to replace config in MAINconfig and PATHconfig

apt-get update && apt-get upgrade
apt-get install python3 python3-pip python3-dev mariadb-server mariadb-client git

#Basemodules
python3 -m pip install mysql-connector-python RPi.GPIO schedule 

#Module for Adafruit DHT22 sensor
python3 -m pip install Adafruit_DHT

#Module for communication with arduino
#python3 -m pip install pyserial

#Module for communication with powerstrip web-consoles
#python3 -m pip install selenium pyvirtualdisplay

#GA code
cd /tmp
git clone https://github.com/growautomation-at/controller.git 
useradd growautomation
mkdir -p /etc/growautomation && cp -r /tmp/controller/agentcode/* !$ && chown -R growautomation !$
ln -s /etc/growautomation/config /usr/local/lib/python3.5/dist-packages/GA
mkdir -p /var/log/growautomation && chown -R growautomation !$´
mkdir -p /mnt/growautomation/backup && chown -R growautomation !$
cp /tmp/controller/setup/standalone/services/growautomation.service /etc/systemd/system/ && systemctl enable growautomation.service




read -p "INFO: Mount backup destination to /mnt/growautomation/backup if backup is needed. Press any key to continue."

#MariaDB setup
read -p "INFO: MariaDB Secure Installation is about to start. Recommended Settings: Y->set secure password,Y,Y,Y,Y"
mysql_secure_installation
mysql -u root -p 
#Sensorconfig
CREATE DATABASE GA0101SENSORS;
USE GA0101SENSORS;
#AHT - AirHumidityTemperatureSensors
CREATE TABLE AHT(
ID INT AUTO_INCREMENT PRIMARY KEY,
DATE DATE,
TIME TIME,
CONTROLLER CHAR(5),
SENSOR CHAR(6),
TEMPERATURE DECIMAL(6,3), 
HUMIDITY DECIMAL(6,3)
);
#EH - EarthHumiditySensors
CREATE TABLE EH(
ID INT AUTO_INCREMENT PRIMARY KEY,
DATE DATE,
TIME TIME,
CONTROLLER CHAR(5),
SENSOR CHAR(5),
HUMIDITY DECIMAL(4)
);

#Actionconfig
CREATE DATABASE GA0101ACTIONS;
USE GA0101ACTIONS;
#PSU - PowerStrip
CREATE TABLE PSU(
ID INT AUTO_INCREMENT PRIMARY KEY,
DATE DATE,
TIME TIME,
CONTROLLER CHAR(5),
ACTIONTAKEN CHAR(40),
OLUSAGE CHAR(10)
);
#WIN - Window Openers
CREATE TABLE WIN(
ID INT AUTO_INCREMENT PRIMARY KEY,
DATE DATE,
TIME TIME,
CONTROLLER CHAR(5),
ACTIONTAKEN CHAR(40),
ACTIONTIME INT(4)
);
#PUMP - Water Pumps
CREATE TABLE PUMP(
ID INT AUTO_INCREMENT PRIMARY KEY,
DATE DATE,
TIME TIME,
CONTROLLER CHAR(5),
ACTIONTAKEN CHAR(40),
ACTIONTIME INT(4)
);

#Note: This setup is not yet finished!
