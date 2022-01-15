# process handler

from core.utils.debug import log
from core.config import shared as config

from subprocess import Popen as subprocessPopen
from subprocess import PIPE as SUBPROCESS_PIPE
from subprocess import TimeoutExpired


def subprocess(command: (list, str), timeout: int = None, out_error: bool = False, logger=log, log_stdout: bool = True):
    logger(f"Executing command \"{command}\"", level=2)

    if timeout is None:
        timeout = config.AGENT.subprocess_timeout

    elif timeout < config.MINIMAL_PROCESS_TIMEOUT:
        logger(f"Got invalid value for process timeout - this might be a configuration issue: '{timeout}'")
        timeout = config.MINIMAL_PROCESS_TIMEOUT

    if type(command) != list:
        command = [command]

    try:
        proc = subprocessPopen(
            command,
            shell=True,
            stdout=SUBPROCESS_PIPE,
            stderr=SUBPROCESS_PIPE
        )
        stdout_bytes, stderr_bytes = proc.communicate(timeout=timeout)
        stdout, stderr = stdout_bytes.decode('utf-8').strip(), stderr_bytes.decode('utf-8').strip()
        exit_code = proc.returncode

    except TimeoutExpired as error:
        stdout = None
        exit_code = 1
        stderr = error

    if exit_code == 0 and stderr in config.NONE_RESULTS:
        stderr = None
        if log_stdout:
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
