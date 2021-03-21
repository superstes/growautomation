#!/usr/bin/python3

# source: https://github.com/superstes/growautomation

# dependencies
#   apt
#     libgpiod2
#   pip
#     adafruit-circuitpython-dht
#   privileges
#     executing user must be a member of group gpio (usermod -a -G gpio USERNAME)
#
# for detailed information see the external documentation:
#   adafruit dht22: https://learn.adafruit.com/dht/dht-circuitpython-code
#
# call:
#   python3 dht22.py $DATA_TYPE "{\"connection\": $GPIO_PIN}"
#  p.e.
#   python3 dht22.py temperature "{\"connection\": 4}"
#   python3 dht22.py humidity "{\"connection\": 8}"

from sys import argv as sys_argv
from time import sleep as time_sleep
from json import loads as json_loads
from json import dumps as json_dumps

import board
from adafruit_dht import DHT22


class Device:
    ARG = sys_argv[1]
    CONFIG = json_loads(sys_argv[2])
    ACCEPTABLE_ARGS = ['temperature', 'humidity']
    PULL_MAX_RETRIES = 5
    PULL_INTERVAL = 3

    def __init__(self):
        self.sensor = DHT22(getattr(board, "D%s" % self.CONFIG['connection']), use_pulseio=False)
        self.data = self._get_data()

    def start(self):
        print(json_dumps(self.data))
        self.sensor.exit()

    def _get_data(self):
        if self.ARG not in self.ACCEPTABLE_ARGS:
            self._error('No acceptable argument passed')

        try_count = 1

        while True:
            if try_count >= self.PULL_MAX_RETRIES:
                self._error('Max retries reached')
            try:
                if self.ARG == 'humidity':
                    data = self.sensor.humidity
                    if self._value_check(data=data, value_max=100, value_min=1):
                        break

                elif self.ARG == 'temperature':
                    data = self.sensor.temperature
                    if self._value_check(data=data, value_max=80, value_min=-15):
                        break
            except RuntimeError as error:
                if str(error).find('Not running on a RPi') != -1:
                    self._error('Executing user is not member of gpio group!')

            time_sleep(self.PULL_INTERVAL)
            try_count += 1

        return {'data': "%.2f" % data}

    @staticmethod
    def _value_check(data, value_max, value_min):
        if value_max > float(data) > value_min:
            return True
        else:
            return False

    @staticmethod
    def _error(msg):
        raise SystemExit(msg)


Device().start()
