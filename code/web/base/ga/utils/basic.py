from datetime import datetime

from packaging.version import parse as parse_version
from packaging.version import Version
from pytz import timezone as pytz_timezone

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


def add_timezone(request, datetime_obj: datetime, tz: str = None, ctz: str = None) -> datetime:
    if ctz is None:
        # takes A LOT of time if done in a loop
        ctz = get_server_config(setting='timezone')

    if tz is not None:
        _tz_aware = datetime_obj.replace(tzinfo=pytz_timezone(tz))
        output = _tz_aware.astimezone(pytz_timezone(ctz))

    else:
        output = datetime_obj.replace(tzinfo=pytz_timezone(ctz))

    return output


def get_datetime_w_tz(request, dt_str: str) -> (None, datetime):  # str datetime to tz-aware datetime obj
    if type(dt_str) != str:
        return None

    try:
        _ts_wo_tz = datetime.strptime(dt_str, DATETIME_TS_FORMAT)
        ts_w_tz = add_timezone(request, datetime_obj=_ts_wo_tz)
        return ts_w_tz

    except ValueError:
        return None


def get_time_difference(time_data: str, time_format: str) -> int:
    before = datetime.strptime(time_data, time_format)
    now = datetime.now()
    difference = now - before

    return int(difference.total_seconds())


def fmt_version(v: (str, float)) -> Version:
    return parse_version(str(v))
