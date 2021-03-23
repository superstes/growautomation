# process handler

from core.utils.debug import Log
from core.config.shared import SUBPROCESS_TIMEOUT

from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from subprocess import TimeoutExpired


def subprocess(command: (list, str), out_error: bool = False, web_ctrl_obj=None):
    if web_ctrl_obj is not None:
        logger = Log(typ='web', web_ctrl_obj=web_ctrl_obj)
        logger.write("Executing command \"%s\"" % command, level=2)

    else:
        logger = Log()
        logger.write("Executing command \"%s\"" % command, level=6)

    if type(command) != list:
        command = [command]

    try:
        output, error = subprocess_popen(
            command,
            shell=True,
            stdout=subprocess_pipe,
            stderr=subprocess_pipe
        ).communicate(timeout=SUBPROCESS_TIMEOUT)

        output, error = output.decode('utf-8').strip(), error.decode('utf-8').strip()

    except TimeoutExpired as error:
        output = None
        error = error

    if error in [None, '']:
        error = None
        logger.write("Process output: \"%s\"" % output, level=6)

    else:
        logger.write("Process error: \"%s\" | output: \"%s\"" % (error, output), level=2)

    if out_error:
        return output, error

    return output


def _filter():
    pass
    # todo: filter for shell commands (security)
