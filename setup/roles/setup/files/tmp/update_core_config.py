#!/usr/bin/python3

# script to update the sql secret in the core config-file

from sys import argv as sys_argv

setting = sys_argv[1]
value = sys_argv[2]

try:
    action = sys_argv[3]

except IndexError:
    action = 'overwrite'

from core.config.object.data.file import GaDataFile

ConfigFile = GaDataFile()
config = ConfigFile.get()

if action == 'overwrite':
    config.update({setting: value})

else:
    # only add the setting if not exists
    if setting not in config:
        config.update({setting: value})

ConfigFile.reset(data=config)
