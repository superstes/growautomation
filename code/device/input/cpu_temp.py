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

output_bin, error_bin = subprocess_popen(
    '/opt/vc/bin/vcgencmd measure_temp',
    shell=True,
    stdout=subprocess_pipe,
    stderr=subprocess_pipe
).communicate()

error = error_bin.decode('utf-8').strip()

if error not in ['', None]:
    if error.find('VCHI initialization failed') != -1:
        raise SystemExit('Executing user is not member of video group')

try:
    output = output_bin.decode('utf-8').strip().split('=', 1)[1].replace("'C", '')
    print(json_dumps({'data': "%.2f" % float(output)}))

except Exception as error:
    print(f"An unexpected error occurred: '{error}'")
