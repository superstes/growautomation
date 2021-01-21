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
        debug = 1
    elif not hard_only:
        try:
            debug = shared_vars.SYSTEM.debug
        except AttributeError:
            debug = shared_vars.STARTUP_DEBUG
    else:
        debug = 0

    if debug == 1:
        prefix = "%s debug:" % now("%H:%M:%S")

        if type(command) == str:
            print(prefix, command)
        elif type(command) == list:
            [print(prefix, call) for call in command]

        return True
    else:
        return False


class Log:
    LOG_TIMESTAMP_FORMAT = "%Y-%m-%d | %H:%M:%S:%f"

    CENSOR_OUTPUT = '●●●●●●●●●'
    SECRET_SETTINGS = ['sql_secret']
    try:
        SECRET_DATA = [shared_vars.SYSTEM.sql_secret]
    except AttributeError:
        SECRET_DATA = []

    def __init__(self, typ: str = 'core'):
        from inspect import stack as inspect_stack
        from inspect import getfile as inspect_getfile
        self.type = typ
        self.name = inspect_getfile((inspect_stack()[1])[0])
        self.log_dir = "%s/%s/%s" % (shared_vars.SYSTEM.path_log, self.type, date_year)
        self.log_file = "%s/%s_%s.log" % (self.log_dir, date_month, self.type)
        self.log_level = shared_vars.SYSTEM.log_level

    def write(self, output: str, level: int = 1) -> bool:
        # log levels:
        #   0 = no; 1 = important error; 2 = errors; 3 = important warning; 4 = warning;
        #   5 = unimportant warning; 6 = info; 7 = unimportant info; 8 = random; 9 = wtf
        if self.type == 'core':
            try:
                if level > self.log_level:
                    return False
            except AttributeError:
                pass
        else:
            if level > self.log_level:
                return False

        self._file()
        output = self._censor(str(output))

        with open("%s/%s_%s.log" % (self.log_dir, date_month, self.type), 'a') as logfile:
            logfile.write("%s - %s - %s\n" % (datetime.now().strftime(self.LOG_TIMESTAMP_FORMAT), self.name, output))

        return True

    def _file(self) -> None:
        if os_path.exists(self.log_dir) is False:
            os_system("mkdir -p %s" % self.log_dir)

        if os_path.exists(self.log_file) is False:
            os_system("touch %s" % self.log_file)

    def _censor(self, output: str) -> str:
        for setting in self.SECRET_SETTINGS:
            if output.find(setting) != -1:
                split_output = output.split(setting)
                updated_list = [split_output[0]]

                for data in split_output[1:]:
                    try:
                        updated_list.append("%s': \"%s\",%s" % (
                                setting,
                                self.CENSOR_OUTPUT,
                                data.split(',', 1)[1]
                            )
                        )
                    except IndexError:
                        output = "LOG ERROR: 'Output has sensitive data (\"%s\") in it that must be censored. " \
                                 "But we were not able to safely censor it. " \
                                 "Output was completely replaced.'" % setting

                if output.find('LOG ERROR') == -1:
                    output = ''.join(updated_list)

        for data in self.SECRET_DATA:
            output.replace(data, self.CENSOR_OUTPUT)

        return output
