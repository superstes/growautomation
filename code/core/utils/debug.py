# logging and debugging

from core.config import shared as config

from datetime import datetime
from os import path as os_path
from pathlib import Path
from inspect import stack as inspect_stack
from inspect import getfile as inspect_getfile
from os import getuid as os_getuid
from os import chmod as os_chmod
from os import chown as os_chown
from grp import getgrnam
from systemd import journal
from time import sleep


def now(time_format: str):
    return datetime.now().strftime(time_format)


class Log:
    def __init__(self, typ: str = 'core', addition: str = None, src_file: str = None):
        self.name = src_file
        if src_file is None:
            self.name = inspect_getfile(inspect_stack()[1][0])

        self.type = typ
        self.log_dir = f"{config.AGENT.path_log}/{self.type}/{now('%Y')}"
        self.log_level = config.AGENT.log_level

        if addition is None:
            self.log_file = f"{self.log_dir}/{now('%m')}_{self.type}.log"

        else:
            self.log_file = f"{self.log_dir}/{now('%m')}_{self.type}_{addition.replace(' ', '_')}.log"

        self.status = self._check()

    def write(self, output: str, level: int = 1, system: bool = False) -> bool:
        # log levels:
        #   0 = no; 1 = important error; 2 = errors; 3 = important warning; 4 = warning;
        #   5 = unimportant warning; 6 = info; 7 = unimportant info; 8 = random; 9 = wtf
        if config.AGENT.debug == 0 and (level > self.log_level or not self.status):
            return False

        output = censor(str(output))

        if system:
            journal.send(output)

        output_formatted = f"{datetime.now().strftime(config.LOG_TIMESTAMP_FORMAT)}{config.LOG_SEPARATOR}{self.name}{config.LOG_SEPARATOR}{output}"
        self._debugger(msg=output_formatted)

        with open(self.log_file, 'a+') as logfile:
            logfile.write(f"{level}{config.LOG_SEPARATOR}{output_formatted}\n")

        return True

    def _check(self) -> bool:
        try:
            if not os_path.exists(self.log_file):
                Path(self.log_dir).mkdir(parents=True, exist_ok=True)
                sleep(0.1)
                os_chown(path=self.log_dir, uid=os_getuid(), gid=getgrnam(config.GA_GROUP)[2])
                os_chmod(path=self.log_dir, mode=int(f'{config.LOG_DIR_PERMS}', base=8))

                with open(self.log_file, 'a+') as logfile:
                    logfile.write('init\n')

            try:
                os_chown(path=self.log_file, uid=os_getuid(), gid=getgrnam(config.GA_GROUP)[2])
                os_chmod(path=self.log_file, mode=int(f'{config.LOG_FILE_PERMS}', base=8))

            except PermissionError:
                # if web tries to change core log-file permissions
                pass

            return True

        except PermissionError as error:
            print(f"LOG ERROR: {censor(error)}")
            return False

    @staticmethod
    def _debugger(msg):
        if config.AGENT.debug == 1:
            print(f'DEBUG: {censor(msg)}')
            return True

        else:
            return False


class MultiLog:
    def __init__(self, log_instances: list):
        self.log_instances = log_instances

    def write(self, output: str, level: int = 1) -> bool:
        result_list = []

        for _log in self.log_instances:
            result_list.append(_log.write(output=output, level=level))

        if all(result_list):
            return True

        return False


def log(output: str, level: int = 1, logger_instance: Log = None, src_file: str = None) -> bool:
    # wrapper function so we don't need always to call the .write method
    if logger_instance is None:
        if src_file is None:
            src_file = inspect_getfile(inspect_stack()[1][0])

        return Log(src_file=src_file).write(output=output, level=level)

    else:
        return logger_instance.write(output=output, level=level)


def fns_log(output: str, level: int = 1) -> bool:
    _src = inspect_getfile(inspect_stack()[1][0])
    return Log(src_file=_src).write(output=output, level=level, system=True)


def web_log(output: str, src_file: str, level: int = 1) -> bool:
    return Log(typ='web', src_file=src_file).write(output=output, level=level)


def device_log(output: str, add: str, level: int = 1) -> bool:
    _src = inspect_getfile(inspect_stack()[1][0])

    if config.AGENT.device_log == 1:
        return MultiLog([
            Log(src_file=_src),
            Log(typ='device', addition=add, src_file=_src)
        ]).write(output=output, level=level)

    else:
        return Log(src_file=_src).write(output=output, level=level)


def censor(output) -> str:
    output = str(output)

    try:
        secrets = [config.AGENT.sql_secret]

    except AttributeError:
        secrets = []

    for setting in config.LOG_SECRET_SETTINGS:
        if output.find(setting) != -1:
            split_output = output.split(setting)
            updated_list = [split_output[0]]

            for data in split_output[1:]:
                try:
                    updated_list.append(f"{setting}': \"{config.LOG_CENSOR_OUTPUT}\",{data.split(',', 1)[1]}")

                except IndexError:
                    output = f"LOG ERROR: 'Output has sensitive data (\"{setting}\") in it that must be censored. " \
                             f"But we were not able to safely censor it. Output was completely replaced.'"

            if output.find('LOG ERROR') == -1:
                output = ''.join(updated_list)

    for secret in secrets:
        output.replace(secret, config.LOG_CENSOR_OUTPUT)

    return output
