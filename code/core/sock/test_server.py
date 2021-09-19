from os import chown
from grp import getgrnam
from pwd import getpwnam
from datetime import datetime

from core.config import shared

shared.init()


class Test:
    security = 0
    log_level = 10
    debug = 1
    path_root = '/var/lib/ga'
    path_log = '/var/log/ga'
    sql_secret = 'placeholder'


try:
    shared.SYSTEM = Test()
    from connect import Server
    Server().run()

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
