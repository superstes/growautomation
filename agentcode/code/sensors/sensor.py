#!/usr/bin/python3

import os

from GA import PATHconfig



os.system("for f in " + PATHconfig.SENSORaht + "; do /usr/bin/python3 \"$f\"; done")

#os.system("for f in " + PATHconfig.SENSOReh + "; do /usr/bin/python3 \"$f\"; done")
