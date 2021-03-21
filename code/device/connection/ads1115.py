#!/usr/bin/python3

# source: https://github.com/superstes/growautomation

# dependencies
#   apt
#     python3-smbus
#     i2c-tools
#   pip
#     adafruit-circuitpython-ads1x15
#   privileges
#     executing user must be a member of groups:
#       gpio (usermod -a -G gpio USERNAME)
#       i2c (usermod -a -G i2c USERNAME)
#   system config
#     enable i2c and reboot:
#       sudo raspi-config nonint do_i2c 0
#
# for detailed information see the external documentation:
#   adafruit i2c: https://learn.adafruit.com/circuitpython-basics-i2c-and-spi/i2c-devices
#   adafruit ads1x15: https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/python-circuitpython
#
# call:
#    python3 ads1115.py None "{\"connection\": $I2C_CONFIG, \"downlink_pin\": $ANALOG_PIN_TO_SENSOR}"
#   p.e.
#    python3 ads1115.py None "{\"connection\": None, \"downlink_pin\": 0}"
#    python3 ads1115.py None "{\"connection\": {\"scl\": \"6\", \"sda\": \"7\"}, \"downlink_pin\": 7}"

from sys import argv as sys_argv
from json import loads as json_loads
from json import dumps as json_dumps
from time import sleep

import board
from busio import I2C
from adafruit_ads1x15 import ads1115
from adafruit_ads1x15.analog_in import AnalogIn


class Device:
    ARG = sys_argv[1]
    CONFIG = json_loads(sys_argv[2])
    MAX_VALUE = 32767
    DATAPOINTS = 10
    DATAPOINT_INTERVAL = 0.1

    def __init__(self):
        self.pin = self.CONFIG['downlink_pin']
        custom_i2c = False

        try:
            i2c = I2C(
                getattr(board, "D%s" % self.CONFIG['connection']['scl']),
                getattr(board, "D%s" % self.CONFIG['connection']['sda'])
            )

            custom_i2c = True

        except (TypeError, KeyError):
            i2c = I2C(board.SCL, board.SDA)

        try:
            self.adc = ads1115.ADS1115(i2c)
        except (ValueError, TimeoutError) as error:
            if str(error).find('No I2C device at address') != -1:
                if custom_i2c:
                    self._error("Connection to ads1115 failed, using custom ports: \"scl=>%s, sda=>%s\", check the wiring and configuration"
                                % (self.CONFIG['connection']['scl'], self.CONFIG['connection']['sda']))
                else:
                    self._error("Connection to ads1115 failed, check the wiring")

        self.data = self._get_data()

    def start(self):
        print(json_dumps({'data': self.data}))

    def _get_data(self):
        self.adc.gain = 1  # could be increased if the data signals are too weak
        device = AnalogIn(self.adc, getattr(ads1115, "P%s" % self.pin))

        return "%.2f" % self._correct_data(device)

    def _correct_data(self, device):
        # corrects output since some data readings might be faulty
        data_list = []
        for _ in range(self.DATAPOINTS):
            data_list.append((100 / self.MAX_VALUE) * device.value)
            sleep(self.DATAPOINT_INTERVAL)

        return sum(data_list) / len(data_list)

    @staticmethod
    def _error(msg):
        raise SystemExit(msg)


Device().start()
