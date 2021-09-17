# process handler

from core.utils.debug import log
from core.config.shared import SUBPROCESS_TIMEOUT

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
        ).communicate(timeout=SUBPROCESS_TIMEOUT)

        output, error = output.decode('utf-8').strip(), error.decode('utf-8').strip()

    except TimeoutExpired as error:
        output = None
        error = error

    if error in [None, '']:
        error = None
        log(f"Process output: \"{output}\"", level=6)

    else:
        log(f"Process error: \"{error}\" | output: \"{output}\"", level=2)

    if out_error:
        return output, error

    return output


def _filter():
    pass
    # todo: filter for shell commands (security)
