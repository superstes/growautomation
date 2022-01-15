from datetime import datetime
from packaging.version import parse as parse_version
from packaging.version import Version
from pytz import timezone as pytz_timezone
from pytz import utc as pytz_utc

from .helper import get_server_config
from ..config.shared import DATETIME_TS_FORMAT


def str_to_list(data: (list, str), reverse: bool = False) -> list:
    if type(data) == str:
        _ = data.split('\n')

    elif data is None:
        _ = []

    else:
        _ = data

    if reverse:
        _.reverse()

    return _


def empty_key(search, param: str) -> bool:
    if param in search and search[param] not in [None, '', "['']", 'None']:
        return False

    return True


def set_key(search, param: str) -> bool:
    return not empty_key(search=search, param=param)


def add_timezone(dt: datetime) -> datetime:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return dt.replace(tzinfo=pytz_timezone(get_server_config(setting='timezone')))

    else:
        # utc is used in storage by django
        return dt.replace(tzinfo=pytz_utc).astimezone(pytz_timezone(get_server_config(setting='timezone')))


def get_dt_w_tz(naive: (str, datetime, None) = None) -> (datetime, None):
    try:
        if naive is None:
            return add_timezone(dt=datetime.now())

        elif type(naive) == str:
            naive = datetime.strptime(naive, DATETIME_TS_FORMAT)

        return add_timezone(dt=naive)

    except ValueError:
        return None


def get_time_difference(time_data: str, time_format: str) -> int:
    before = datetime.strptime(time_data, time_format)
    now = datetime.now()
    difference = now - before

    return int(difference.total_seconds())


def fmt_version(v: (str, float)) -> Version:
    return parse_version(str(v))
