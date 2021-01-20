#!/usr/bin/python3

# dependencies
#   apt
#     python3-smbus
#   pip
#     adafruit-circuitpython-mcp3xxx
#   privileges
#     executing user must be a member of group gpio (usermod -a -G gpio USERNAME)
#   system config
#     enable spi and reboot:
#       sudo raspi-config nonint do_spi 0
#
# for detailed information see the external documentation:
#   adafruit spi: https://learn.adafruit.com/circuitpython-basics-i2c-and-spi/spi-devices
#   adafruit mcp3xxx: https://learn.adafruit.com/mcp3008-spi-adc/python-circuitpython
#
# call:
#   python3 mcp3008.py $SPI_NUMBER "{\"connection\": $GPIO_PIN_TO_ADC, \"downlink_pin\": $ANALOG_PIN_TO_SENSOR}"
#  p.e.
#   python3 mcp3008.py 0 "{\"connection\": 8, \"downlink_pin\": 0}"

from sys import argv as sys_argv
from json import loads as json_loads
from json import dumps as json_dumps
from time import sleep

import board
from digitalio import DigitalInOut
from busio import SPI
from adafruit_mcp3xxx import mcp3008
from adafruit_mcp3xxx.analog_in import AnalogIn


class Device:
    ARG = int(sys_argv[1])
    CONFIG = json_loads(sys_argv[2])
    MAX_VALUE = 65535
    DATAPOINTS = 10
    DATAPOINT_INTERVAL = 0.1
    MAX_NULL_VALUE = 5
    MIN_VOLTAGE = 0.1
    MIN_VALUE = 1

    def __init__(self):
        self.connection = self.CONFIG['connection']
        self.pin = self.CONFIG['downlink_pin']
        spi_nr = self.ARG

        if spi_nr == 0:
            spi = SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        else:
            spi = SPI(clock=board.SCK_1, MISO=board.MISO_1, MOSI=board.MOSI_1)

        pin_dig = getattr(board, "D%s" % self.connection)
        cs = DigitalInOut(pin_dig)
        self.mcp = mcp3008.MCP3008(spi_bus=spi, cs=cs)
        self.data = self._get_data()

    def start(self):
        print(json_dumps({'data': self._get_data()}))

    def _get_data(self):
        device = AnalogIn(self.mcp, getattr(mcp3008, "P%s" % self.pin))

        return "%.2f" % self._correct_data(device)

    def _correct_data(self, device):
        # corrects output since some data readings might be faulty
        data_list = []
        for _ in range(self.DATAPOINTS):
            voltage = 0.0
            value = 0
            count = 1

            while voltage < self.MIN_VOLTAGE or value == 0:
                if count > self.MAX_NULL_VALUE:
                    break

                value, voltage = device.value, device.voltage
                count += 1

            if voltage < self.MIN_VOLTAGE or value == 0:
                continue

            data_list.append((100 / self.MAX_VALUE) * value)
            sleep(self.DATAPOINT_INTERVAL)

        return sum(data_list) / len(data_list)


Device().start()
