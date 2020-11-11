# special processing of single-conditions

from core.utils.debug import debugger

from datetime import datetime

SPECIAL_TIME_FORMAT = '%H:%M:%S'
SPECIAL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def special(condition) -> tuple:
    speci = condition.special

    debugger("device-output-condition-proc-singlespecial | _special | condition '%s', specialtype '%s'"
             % (condition.name, speci))

    if speci in ['time', 'datetime']:
        error, data, value = _time(condition=condition)
    else:
        error = True

    if error:
        # log error or whatever
        debugger("device-output-condition-proc-singlespecial | _special | condition '%s' has an unsupported "
                 "special type '%s'" % (condition.name, speci))
        raise KeyError("Condition '%s' has an unsupported special type '%s" % (condition.name, speci))

    debugger("device-output-condition-proc-singlespecial | _special | condition '%s', specialtype '%s', "
             "data '%s', value '%s'" % (condition.name, speci, data, value))

    return data, value


def _time(condition) -> tuple:
    speci = condition.special
    data = datetime.now()
    error = False

    if speci == 'time':
        value = datetime.strptime(condition.condition_value, SPECIAL_TIME_FORMAT)
    elif speci == 'datetime':
        value = datetime.strptime(condition.condition_value, SPECIAL_DATETIME_FORMAT)
    else:
        error = True
        value = None

    return error, data, value
