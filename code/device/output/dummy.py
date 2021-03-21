#!/usr/bin/python3

# source: https://github.com/superstes/growautomation

# output test-script
#
# call:
#    python3 dummy.py $ARG "{\"connection\": $PIN|GPIO|GENERIC}"

from sys import argv as sys_argv
from json import loads as json_loads
from datetime import datetime


class Device:
    ARG = sys_argv[1]
    CONFIG = json_loads(sys_argv[2])
    LOGFILE = '/tmp/ga_output_dummy.log'
    TIME_FORMAT = '%Y-%m-%d | %H:%M:%S:%f'

    def start(self):
        self.test_log('Script started')
        self.test_log(f"Argument: '{self.ARG}'")
        self.test_log(f"Config: '{self.CONFIG}'")
        self.test_log('Script finished')

    @classmethod
    def test_log(cls, out: str):
        with open(cls.LOGFILE, 'a') as log:
            log.write(f"{datetime.now().strftime(cls.TIME_FORMAT)} - {out}")

    @staticmethod
    def _error(msg):
        raise SystemExit(msg)


Device().start()
