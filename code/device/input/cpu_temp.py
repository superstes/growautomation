#!/usr/bin/python3

# source: https://github.com/superstes/growautomation

# dependencies
#   privileges
#     executing user must be a member of group video (usermod -a -G video USERNAME)
#
# call:
#   python3 cpu_temp.py

from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from json import dumps as json_dumps

STDOUT_BYTES, STDERR_BYTES = subprocess_popen(
    '/opt/vc/bin/vcgencmd measure_temp',
    shell=True,
    stdout=subprocess_pipe,
    stderr=subprocess_pipe
).communicate()

STDOUT = STDOUT_BYTES.decode('utf-8').strip()
STDERR = STDERR_BYTES.decode('utf-8').strip()

if STDERR not in ['', None]:
    if STDERR.find('VCHI initialization failed') != -1:
        raise SystemExit("The executing user is not member of the 'video' group")

try:
    output = STDOUT.split('=', 1)[1].replace("'C", '')
    print(json_dumps({'data': "%.2f" % float(output)}))

except Exception as error:
    print(f"An unexpected error occurred: '{error}'")
