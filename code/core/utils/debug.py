# provides:
#   shell debugging
#   error logging

from core.config import shared as shared_vars

from datetime import datetime
from os import system as os_system
from os import path as os_path


def now(time_format: str):
    return datetime.now().strftime(time_format)


date_year, date_month = now("%Y"), now("%m")


def debugger(command, hard_debug: bool = False, hard_only: bool = False, level: int = 1) -> bool:
    if level > 1:
        return False
    if hard_debug:
        debug = True
    elif not hard_only:
        try:
            debug = shared_vars.SYSTEM.debug
        except AttributeError:
            debug = shared_vars.STARTUP_DEBUG
    else:
        debug = False

    if debug is True:
        prefix = "%s debug:" % now("%H:%M:%S")

        if type(command) == str:
            print(prefix, command)
        elif type(command) == list:
            [print(prefix, call) for call in command]

        return True
    else:
        return False


class Log:
    def __init__(self, typ: str = 'core'):
        from inspect import stack as inspect_stack
        from inspect import getfile as inspect_getfile
        self.type = typ
        self.name = inspect_getfile((inspect_stack()[1])[0])
        self.log_dir = "%s/%s/%s" % (shared_vars.SYSTEM.path_log, self.type, date_year)
        self.log_file = "%s/%s_%s.log" % (self.log_dir, date_month, self.type)
        self.log_level = shared_vars.SYSTEM.log_level

    def _censor(self):
        return False
        # censor passwords -> check for strings in output ('IDENTIFIED by', 'pwd', 'password')

    def write(self, output: str, level: int = 1) -> bool:
        if self.type == 'core':
            try:
                if level > self.log_level:
                    return False
            except AttributeError:
                pass
        else:
            if level > self.log_level:
                return False
        if os_path.exists(self.log_dir) is False:
            os_system("mkdir -p %s" % self.log_dir)

        with open("%s/%s_%s.log" % (self.log_dir, date_month, self.type), 'a') as logfile:
            logfile.write("%s - %s - %s\n" % (datetime.now().strftime("%H:%M:%S:%f"), self.name, output))

        return True

    def file(self) -> str:
        if os_path.exists(self.log_dir) is False:
            os_system("mkdir -p %s" % self.log_dir)

        if os_path.exists(self.log_file) is False:
            os_system("touch %s" % self.log_file)

        return self.log_file
