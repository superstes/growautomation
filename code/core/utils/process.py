# process handler

from core.utils.debug import log
from core.config import shared as config

from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from subprocess import TimeoutExpired


def subprocess(command: (list, str), out_error: bool = False, logger=log):
    logger(f"Executing command \"{command}\"", level=2)

    if type(command) != list:
        command = [command]

    try:
        proc = subprocess_popen(
            command,
            shell=True,
            stdout=subprocess_pipe,
            stderr=subprocess_pipe
        )
        stdout_bytes, stderr_bytes = proc.communicate(timeout=config.AGENT.subprocess_timeout)
        stdout, stderr = stdout_bytes.decode('utf-8').strip(), stderr_bytes.decode('utf-8').strip()
        exit_code = proc.returncode

    except TimeoutExpired as error:
        stdout = None
        exit_code = 1
        stderr = error

    if exit_code == 0 and stderr in config.NONE_RESULTS:
        stderr = None
        if not logger(f"Got output by processing command \"{command}\": \"{stdout}\"", level=7):
            logger(f"Process output: \"{stdout}\"", level=6)

    else:
        logger(f"Got error while processing command \"{command}\": "
               f"exit-code {exit_code} - \"{stderr}\" | output: \"{stdout}\"", level=2)

    if out_error:
        return stdout, stderr

    return stdout


def _filter():
    pass
    # todo: filter for shell commands (security)
