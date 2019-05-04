#!/bin/bash
sudo apt-get update && apt-get upgrade && apt-get dist-upgrade
sudo apt-get install python3
sudo apt-get install python3-pip python3-dev mysql-server mysql-client git
sudo python3 -m pip install mysql-connector-python pyserial Adafruit_DHT RPi.GPIO spidev
sudo mkdir -p /etc/growautomation-at/download 
cd !$
sudo git clone https://github.com/growautomation-at/standalone-controller.git
