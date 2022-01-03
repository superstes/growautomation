#!/usr/bin/python3

# script to update the sql secret in the core config-file

from sys import argv as sys_argv

secret = sys_argv[1]

from core.config.object.data.file import GaDataFile

ConfigFile = GaDataFile()
config = ConfigFile.get()
config.update({'sql_secret': secret})
ConfigFile.reset(data=config)
