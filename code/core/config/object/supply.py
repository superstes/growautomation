# prepares data for factory
#  gets db connection data from config file object
#  loads data from db

from .data.file import GaDataFile
from .data.db import GaDataDb


def get_db_config():
    dbconnection = GaDataDb(GaDataFile().get())


