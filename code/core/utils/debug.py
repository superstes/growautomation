# logging and debugging

from core.config import shared as shared_vars
from core.config.web_shared import init as web_shared_vars

from datetime import datetime
from os import getuid as os_getuid
from os import path as os_path
from pathlib import Path
from os import chmod as os_chmod
from os import chown as os_chown


def now(time_format: str):
    return datetime.now().strftime(time_format)


date_year, date_month = now("%Y"), now("%m")


class Log:
    try:
        SECRET_DATA = [shared_vars.SYSTEM.sql_secret]

    except AttributeError:
        SECRET_DATA = []

    def __init__(self, typ: str = 'core', addition: str = None, web_ctrl_obj=None, src_file: str = None):
        self.name = src_file
        if src_file is None:
            from inspect import stack as inspect_stack
            from inspect import getfile as inspect_getfile
            self.name = inspect_getfile(inspect_stack()[1][0])

        self.type = typ

        if web_ctrl_obj is not None:
            web_shared_vars(web_ctrl_obj)

        self.log_dir = f"{shared_vars.SYSTEM.path_log}/{self.type}/{date_year}"
        self.log_level = shared_vars.SYSTEM.log_level

        if addition is None:
            self.log_file = f"{self.log_dir}/{date_month}_{self.type}.log"

        else:
            self.log_file = f"{self.log_dir}/{date_month}_{self.type}_{addition}.log"

        self.status = self._check()

    def write(self, output: str, level: int = 1) -> bool:
        # log levels:
        #   0 = no; 1 = important error; 2 = errors; 3 = important warning; 4 = warning;
        #   5 = unimportant warning; 6 = info; 7 = unimportant info; 8 = random; 9 = wtf

        if shared_vars.SYSTEM.debug == 1:
            level = 10

        if level > self.log_level or not self.status:
            return False

        output = self._censor(str(output))
        output_formatted = f"{datetime.now().strftime(shared_vars.LOG_TIMESTAMP_FORMAT)}{shared_vars.LOG_SEPARATOR}{self.name}{shared_vars.LOG_SEPARATOR}{output}"
        self._debugger(command=output_formatted)

        with open(self.log_file, 'a+') as logfile:
            logfile.write(f"{level}{shared_vars.LOG_SEPARATOR}{output_formatted}\n")

        return True

    def _check(self) -> bool:
        try:
            if not os_path.exists(self.log_file):
                Path(self.log_dir).mkdir(parents=True, exist_ok=True)

                with open(self.log_file, 'a+') as logfile:
                    logfile.write('init')

            os_chown(path=self.log_file, uid=os_getuid(), gid=shared_vars.GA_GROUP)
            os_chmod(path=self.log_file, mode=int(f'{shared_vars.LOG_FILE_PERMS}', base=8))

            return True

        except PermissionError:
            print(f"LOG ERROR: Unable to access/modify log file '{self.log_file}'")
            return False

    def _censor(self, output: str) -> str:
        for setting in shared_vars.LOG_SECRET_SETTINGS:
            if output.find(setting) != -1:
                split_output = output.split(setting)
                updated_list = [split_output[0]]

                for data in split_output[1:]:
                    try:
                        updated_list.append(f"{setting}': \"{shared_vars.LOG_CENSOR_OUTPUT}\",{data.split(',', 1)[1]}")

                    except IndexError:
                        output = f"LOG ERROR: 'Output has sensitive data (\"{setting}\") in it that must be censored. " \
                                 f"But we were not able to safely censor it. Output was completely replaced.'"

                if output.find('LOG ERROR') == -1:
                    output = ''.join(updated_list)

        for data in self.SECRET_DATA:
            output.replace(data, shared_vars.LOG_CENSOR_OUTPUT)

        return output

    @staticmethod
    def _debugger(command):
        if shared_vars.SYSTEM.debug == 1:
            print(f'DEBUG: {command}')
            return True

        else:
            return False


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
        from systemd import journal as systemd_journal

        if level == 1:
            systemd_journal.write(output)

        return self.log.write(output=output, level=level)
