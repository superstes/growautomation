# special processing of single-conditions

from core.device.log import device_logger

from datetime import datetime

SPECIAL_TIME_FORMAT = '%H:%M:%S'
SPECIAL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


# todo: refactor it => Ticket#23


def special(condition, device: str) -> tuple:
    logger = device_logger(addition=device)
    speci = condition.special

    logger.write("Condition \"%s\" has a special-type set: \"%s\"" % (condition.name, speci), level=9)

    if speci in ['time', 'datetime']:
        error, data, value = _time(condition=condition)

        if not error:
            logger.write("Condition \"%s\" with specialtype \"%s\" got data \"%s\", value \"%s\"" % (condition.name, speci, data, value))

            return data, value

    logger.write("Condition \"%s\" has an unsupported special-type set: \"%s\"" % (condition.name, speci), level=5)
    raise KeyError("Condition \"%s\" has an unsupported special-type set \"%s\"" % (condition.name, speci))


def _time(condition) -> tuple:
    speci = condition.special
    data = datetime.now()
    error = False

    if speci == 'time':
        value = datetime.strptime(condition.value, SPECIAL_TIME_FORMAT)
    elif speci == 'datetime':
        value = datetime.strptime(condition.value, SPECIAL_DATETIME_FORMAT)
    else:
        error = True
        value = None

    return error, data, value
