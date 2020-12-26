from sys import platform
from datetime import datetime


def check_develop() -> bool:
    if platform == 'win32':
        return True

    else:
        return False


def get_time_difference(time_data: str, time_format: str) -> int:
    before = datetime.strptime(time_data, time_format)
    now = datetime.now()
    difference = now - before

    return int(difference.total_seconds())
