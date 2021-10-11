# process handler

from core.utils.debug import log
from core.config import shared as config

from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from subprocess import TimeoutExpired


def subprocess(command: (list, str), out_error: bool = False):
    log(f"Executing command \"{command}\"", level=2)

    if type(command) != list:
        command = [command]

    try:
        output, error = subprocess_popen(
            command,
            shell=True,
            stdout=subprocess_pipe,
            stderr=subprocess_pipe
        ).communicate(timeout=config.SUBPROCESS_TIMEOUT)

        output, error = output.decode('utf-8').strip(), error.decode('utf-8').strip()

    except TimeoutExpired as error:
        output = None
        error = error

    if error in config.NONE_RESULTS:
        error = None
        if not log(f"Got output by processing command \"{command}\": \"{output}\"", level=7):
            log(f"Process output: \"{output}\"", level=6)

    else:
        log(f"Got error while processing command \"{command}\": \"{error}\" | output: \"{output}\"", level=2)

    if out_error:
        return output, error

    return output


def _filter():
    pass
    # todo: filter for shell commands (security)
