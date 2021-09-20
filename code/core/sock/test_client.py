from os import chown
from grp import getgrnam
from pwd import getpwnam
from time import sleep
from datetime import datetime

from core.config import shared

# NOTE: the script must be executed as ga-serviceuser; else you will find that no logs can be written by the service while it is executing

shared.init()


class Test:
    security = 0
    log_level = 0
    debug = 0
    path_root = '/var/lib/ga'
    path_log = '/var/log/ga'
    sql_secret = 'placeholder'


try:
    shared.SYSTEM = Test()
    from connect import Client
    print(Client(path='ga.core.device.input.1').post(data='start'))
    sleep(0.2)

except KeyboardInterrupt:
    pass


def now(time_format: str):
    return datetime.now().strftime(time_format)


date_year, date_month = now("%Y"), now("%m")
chown(
    path=f'{shared.SYSTEM.path_log}/core/{date_year}/{date_month}_core.log',
    uid=getpwnam('ga_core').pw_uid,
    gid=getgrnam('ga')[2]
)
