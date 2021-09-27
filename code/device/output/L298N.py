#!/usr/bin/python3

# source: https://github.com/superstes/growautomation

# dependencies
#   privileges
#     executing user must be a member of group gpio (usermod -a -G gpio USERNAME)
#
# call:
#    python3 L298N.py forward/reverse "{\"connection\": $FWD+REV-PINS+RUNTIME}"
#   p.e.
#    python3 L298N.py forward "{\"connection\": {\"fwd\": \"21\", \"rev\": \"20\", \"time\": \"60\"}}"
#    python3 L298N.py reverse "{\"connection\": {\"fwd\": \"8\", \"rev\": \"7\", \"pwm\": \"25\", \"time\": \"15\"}}"

from sys import argv as sys_argv
from json import loads as json_loads
import RPi.GPIO as GPIO
from time import sleep
from traceback import print_exc


class Device:
    ACTION = sys_argv[1]
    CONFIG = json_loads(sys_argv[2])

    SUPPORTED_ACTIONS = ['forward', 'reverse']

    def __init__(self):
        try:
            # we have no support to provide the pwm speed/percentage yet.. could be done by providing another argument
            self.pin_pwm = int(self.CONFIG['connection']['pwm'])

        except KeyError:
            # if not supplied => we'll assume that it is already connected to 3.3V
            self.pin_pwm = None

        try:
            self.pin_fwd = int(self.CONFIG['connection']['fwd'])
            self.pin_rev = int(self.CONFIG['connection']['rev'])
            self.runtime = int(self.CONFIG['connection']['time'])

        except KeyError as error:
            self._error(f"At least one of the following arguments was not supported: fwd, rev, time\n"
                        f"Error: '{error}'")

        if self.ACTION not in self.SUPPORTED_ACTIONS:
            self._error(f"Got unsupported action \"{self.ACTION}\" -> must be one of \"{self.SUPPORTED_ACTIONS}\"")

    def start(self):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin_fwd, GPIO.OUT)
            GPIO.setup(self.pin_rev, GPIO.OUT)

            if self.pin_pwm is not None:
                GPIO.setup(self.pin_pwm, GPIO.OUT)
                GPIO.output(self.pin_pwm, GPIO.HIGH)

            if self.ACTION == 'forward':
                GPIO.output(self.pin_fwd, GPIO.HIGH)
                GPIO.output(self.pin_rev, GPIO.LOW)

            else:
                GPIO.output(self.pin_fwd, GPIO.LOW)
                GPIO.output(self.pin_rev, GPIO.HIGH)

            sleep(self.runtime)

            self._cleanup()

        except (Exception, KeyboardInterrupt) as error:
            self._cleanup()

            if str(error).find('Not running on a RPi') != -1:
                self._error("The executing user is not member of the 'gpio' group!")

            self._error(msg=f"Got unexpected error: \"{error}\"\n{print_exc()}")

    def _cleanup(self):
        if self.pin_pwm is not None:
            GPIO.output(self.pin_pwm, GPIO.LOW)

        GPIO.output(self.pin_fwd, GPIO.LOW)
        GPIO.output(self.pin_rev, GPIO.LOW)
        GPIO.cleanup()

    @staticmethod
    def _error(msg):
        raise SystemExit(msg)


Device().start()
