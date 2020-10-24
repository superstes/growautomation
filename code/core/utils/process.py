# process handler



class Multi:
    def __init__(self):
        pass


def subprocess(command, out_error=False, debug=False):
    from subprocess import Popen as subprocess_popen
    from subprocess import PIPE as subprocess_pipe

#    if debug: debugger(command="smallant - process |input: '%s'" % command, hard_debug=True)

    output, error = subprocess_popen([command], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
    output, error = output.decode('utf-8').strip(), error.decode('utf-8').strip()

#    if debug: debugger(command="smallant - process |output: '%s' '%s' |error: '%s' '%s'"
#                               % (type(output), output, type(error), error), hard_debug=True)

    if out_error is False:
        return output
    else:
        return output, error