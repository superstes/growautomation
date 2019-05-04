#!/bin/bash
apt-get update && apt-get upgrade && apt-get dist-upgrade
apt-get install python3 python3-pip python3-dev mysql-server mysql-client git
python3 -m pip install mysql-connector-python pyserial Adafruit_DHT RPi.GPIO spidev
mkdir -p /etc/growautomation-at/download 
cd !$
git clone https://github.com/growautomation-at/standalone-controller.git
mysql_secure_installation
#Note: This setup is not finished!
