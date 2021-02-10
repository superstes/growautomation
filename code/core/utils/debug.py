# provides:
#   shell debugging
#   error logging

from core.config import shared as shared_vars

from datetime import datetime
from os import system as os_system
from os import path as os_path
from systemd import journal as systemd_journal


def now(time_format: str):
    return datetime.now().strftime(time_format)


date_year, date_month = now("%Y"), now("%m")


def debugger(command) -> bool:
    debug = shared_vars.SYSTEM.debug

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
    LOG_TIMESTAMP_FORMAT = '%Y-%m-%d | %H:%M:%S:%f'

    CENSOR_OUTPUT = '●●●●●●●●●'
    SECRET_SETTINGS = ['sql_secret']
    try:
        SECRET_DATA = [shared_vars.SYSTEM.sql_secret]
    except AttributeError:
        SECRET_DATA = []

    def __init__(self, typ: str = 'core', addition: str = None):
        from inspect import stack as inspect_stack
        from inspect import getfile as inspect_getfile
        self.type = typ
        self.name = inspect_getfile((inspect_stack()[1])[0])
        self.log_dir = "%s/%s/%s" % (shared_vars.SYSTEM.path_log, self.type, date_year)
        if addition is None:
            self.log_file = "%s/%s_%s.log" % (self.log_dir, date_month, self.type)
        else:
            self.log_file = "%s/%s_%s_%s.log" % (self.log_dir, date_month, self.type, addition)
        self.log_level = shared_vars.SYSTEM.log_level
        self._file()

    def write(self, output: str, level: int = 1) -> bool:
        # log levels:
        #   0 = no; 1 = important error; 2 = errors; 3 = important warning; 4 = warning;
        #   5 = unimportant warning; 6 = info; 7 = unimportant info; 8 = random; 9 = wtf

        if shared_vars.SYSTEM.debug == 1:
            level = 9

        if self.type == 'core':
            try:
                if level > self.log_level:
                    return False
            except AttributeError:
                pass
        else:
            if level > self.log_level:
                return False

        output = self._censor(str(output))

        output_formatted = "%s - %s - %s" % (datetime.now().strftime(self.LOG_TIMESTAMP_FORMAT), self.name, output)

        debugger(command=output_formatted)

        with open(self.log_file, 'a') as logfile:
            logfile.write("%s - %s\n" % (level, output_formatted))

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


class MultiLog:
    def __init__(self, log_instances: list):
        self.log_instances = log_instances

    def write(self, output: str, level: int = 1) -> bool:
        result_list = []

        for log in self.log_instances:
            result_list.append(log.write(output=output, level=level))

        if all(result_list):
            return True

        return False


class FileAndSystemd:
    def __init__(self, log_instance):
        self.log = log_instance

    def write(self, output: str, level: int = 1) -> bool:
        if level == 1:
            systemd_journal.write(output)

        return self.log.write(output=output, level=level)
