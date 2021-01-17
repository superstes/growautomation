#!/usr/bin/python3

# dependencies
#   apt
#     python3-smbus
#     i2c-tools
#   pip
#     adafruit-circuitpython-ads1x15
#   privileges
#     executing user must be a member of group gpio (usermod -a -G gpio USERNAME)
#   system config
#     enable i2c and reboot:
#       sudo sed -i 's/#dtparam=i2c_arm=on/dtparam=i2c_arm=on/g' /boot/config.txt

from sys import argv as sys_argv
from json import loads as json_loads
from json import dumps as json_dumps

import board
from busio import I2C
from adafruit_ads1x15 import ads1115
from adafruit_ads1x15.analog_in import AnalogIn


class Device:
    ARG = sys_argv[1]
    CONFIG = json_loads(sys_argv[2])
    MAX_VALUE = 32767

    def __init__(self):
        i2c = I2C(board.SCL, board.SDA)
        self.adc = ads1115.ADS1115(i2c)

        if 'input' in self.CONFIG:
            self.input_type = self.CONFIG['input']
        else:
            self.input_type = None

        self.data = self._get_data()

    def start(self):
        print(json_dumps({'data': self.data}))

    def _get_data(self):
        try:
            self.adc.gain = 1  # could be increased if the data signals are too weak

            data = AnalogIn(self.adc, getattr(ads1115, "P%s" % self.CONFIG['connection']))

            refactored_data = self._percentage(data=data.value)
        except RuntimeError as error:
            if str(error).find('Not running on a RPi') != -1:
                self._error('Executing user is not member of gpio group!')

            return None

        return "%.2f" % refactored_data

    @staticmethod
    def _error(msg):
        raise SystemExit(msg)

    def _percentage(self, data: int) -> float:
        if self.input_type == 'csmsv1.2':
            # todo: how to set the hardcoded input_type when naming is free
            return self._fix_value_capacitive_moisture(data)
        else:
            _ = (100 / self.MAX_VALUE) * data
            return _

    def _fix_value_capacitive_moisture(self, value: int) -> float:
        # capacitive moisture sensor v1.2
        #   the sensor does not use the full value range
        #   if 3.3V is used it will set between ~2.8V and ~1.5V
        #   for more info see: https://thecavepearlproject.org/2020/10/27/hacking-a-capacitive-soil-moisture-sensor-for-frequency-output/
        #   should be: 100% = soaking wet; 0% = desert dry
        soaking_percent = 50
        desert_percent = 85

        value_range_min = (self.MAX_VALUE / 100) * soaking_percent
        value_range_max = (self.MAX_VALUE / 100) * desert_percent
        value_range = value_range_max - value_range_min

        if value > value_range_max:
            _value = value_range
        else:
            _value = value - value_range_min

        _ = 100 / value_range
        percentage = 100 - (_ * _value)

        return percentage


Device().start()
