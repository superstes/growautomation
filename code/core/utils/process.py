# process handler

from core.utils.debug import debugger

from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe

from json import dumps


class Multi:
    def __init__(self):
        pass


def subprocess(command, out_error=False, debug=False):
    debugger("utils-process | subprocess | executing command '%s'" % command)

    # output, error = subprocess_popen([command], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
    # output, error = output.decode('utf-8').strip(), error.decode('utf-8').strip()

    output = dumps({'data': 'testdata'})
    error = None

    debugger("utils-process | subprocess | output '%s'; error '%s'" % (output, error))

    if out_error is False:
        return output
    else:
        return output, error
