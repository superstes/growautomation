# process handler

from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe

TIMEOUT = 10


def subprocess(command, out_error=False, debug=False):
    if type(command) != list:
        command = [command]
    try:
        output, error = subprocess_popen(
            command,
            shell=True,
            stdout=subprocess_pipe,
            stderr=subprocess_pipe
        ).communicate(timeout=TIMEOUT)
    except subprocess.TimeoutExpired as error:
        output = None

    output, error = output.decode('utf-8').strip(), error.decode('utf-8').strip()

    if error is not None:  # might not be None since i decoded it
        pass
        # log error or whatever

    if out_error is False:
        return output
    else:
        return output, error
