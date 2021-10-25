#!/usr/bin/python3.9
# This file is part of GrowAutomation
#     Copyright (C) 2021  René Pascal Rath
#
#     GrowAutomation is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#     E-Mail: contact@growautomation.at
#     Web: https://github.com/superstes/growautomation

# ga_version 1.0

# environmental variable PYTHONPATH must be set to the growautomation root-path for imports to work
#   (export PYTHONPATH=/var/lib/ga)
#   it's being set automatically by the systemd service

from core.utils.test import test_tcp_stream
from core.config import shared_init_prestart as startup_shared_vars
from core.config import shared as config

from systemd import journal
from sys import exc_info as sys_exc_info
from os import path as os_path
from os import stat as os_stat
from os import getuid as os_getuid
from os import environ as os_environ
from pathlib import Path
import signal
from traceback import format_exc
from datetime import datetime
from grp import getgrnam
from os import chmod as os_chmod
from os import chown as os_chown


class Prepare:
    def __init__(self):
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT, self._stop)
        signal.signal(signal.SIGUSR1, self._stop)
        self.debug = False
        self.logger = None
        self.log_cache = []

        if 'GA_GROUP' in os_environ:
            group = os_environ['GA_GROUP']

        else:
            group = config.GA_GROUP

        self.uid = os_getuid()
        self.ga_gid = getgrnam(group)[2]

    def start(self):
        self._log('Starting service initialization.')

        if self._check_file_config():
            startup_shared_vars.init()
            if self._check_file_log():
                from core.utils.debug import Log, FileAndSystemd
                self.logger = FileAndSystemd(Log())
                if self._check_networking():
                    if self._check_database():
                        if self._check_factory():
                            self._log('Finished service pre-checks successfully.')

                        else:
                            self._error('Factory check failed! Unable to start service!!')

                    else:
                        self._error('Database check failed! Unable to start service!!')

                else:
                    self._error('Network check failed! Unable to start service!!')

            else:
                self._error('Log file check failed! Unable to start service!!')

        else:
            self._error('Config file check failed! Unable to start service!!')

    def _stop(self, signum=None, stack=None):
        if signum is not None:
            try:
                self._log(f"Service received signal {signum} - \"{sys_exc_info()[0].__name__}\"", level=3)

            except AttributeError:
                self._log(f"Service received signal {signum}", level=3)

        self._log('Service stopped.')

    def _check_file_config(self) -> bool:
        service_dir = Path(__file__).parent.absolute()
        subtract_to_root = 2  # how many dirs are it to get from here down to the ga root path
        ga_root_path = '/'.join(str(service_dir).split('/')[:-subtract_to_root])

        return self._check_file(
            files={
                'config': {
                    'path': f'{ga_root_path}/core/config/file/core.conf',
                    'type': 'text',
                    'access': 'rw',
                    'perms': 640,
                    'owner': self.uid,
                    'group': self.ga_gid,
                    'exists': True,
                },
                'secret': {
                    'path': f'{ga_root_path}/core/secret/random.key',
                    'type': 'text',
                    'access': 'r',
                    'perms': 440,
                    'owner': self.uid,
                    'group': self.ga_gid,
                    'exists': True,
                },
            }
        )

    def _check_file_log(self) -> bool:
        return self._check_file(
            files={
                'log': {
                    'path': f'{config.AGENT.path_log}/core/{datetime.now().strftime("%Y")}/{datetime.now().strftime("%m")}_core.log',
                    'type': 'text',
                    'access': 'rw',
                    'perms': 644,
                    'owner': self.uid,
                    'group': self.ga_gid,
                    'exists': False,
                }
            }
        )

    def _check_file(self, files: dict) -> bool:
        result_dict = {}

        for file, config in files.items():
            path = config['path']
            result_dict[file] = False

            if not os_path.exists(path) and not config['exists']:
                result_dict[file] = True

            elif os_path.exists(path):
                perms = int(oct(os_stat(path).st_mode)[-3:])
                owner_perm, group_perm, other_perm = [int(num) for num in str(perms)]

                owner = os_stat(path).st_uid
                group = os_stat(path).st_gid

                if perms != config['perms'] or owner != config['owner'] or group != config['group']:
                    self._log(f"Permissions for file \"{path}\" are not set as expected")
                    self._log(
                        f"Permissions for file \"{path}\" are \"{owner = }, {group = }, {perms= }\" "
                        f"but should be \"owner = {config['owner']}, group = {config['group']}, perms = {config['perms']}\"",
                        level=6
                    )

                    # extended check
                    if config['access'] == 'rw':
                        target_perm = 6

                    else:
                        target_perm = 4

                    sub_check_dict = {'owner': False, 'group': False, 'other': False}

                    if owner == config['owner'] and owner_perm == target_perm:
                        sub_check_dict['owner'] = True

                    if owner == config['group'] and group_perm == target_perm:
                        sub_check_dict['group'] = True

                    if other_perm == target_perm:
                        sub_check_dict['other'] = True

                    if not all(sub_check_dict.values()):
                        try:
                            os_chown(path=path, uid=config['owner'], gid=config['group'])
                            os_chmod(path=path, mode=int(f"{config['perms']}", base=8))
                            result_dict[file] = True

                        except PermissionError:
                            self._log(f"Failed to set permissions for file \"{path}\"")
                            self._log(f"{format_exc(limit=config.LOG_MAX_TRACEBACK_LENGTH)}")
                            result_dict[file] = False

                if 'type' in config and config['type'] == 'text':
                    if config['access'] == 'rw':
                        try:
                            with open(path, 'r+') as _:
                                _data = _.read()

                            result_dict[file] = True

                        except PermissionError:
                            self._log(f"Failed to open file \"{path}\" for writing")
                            self._log(f"{format_exc(limit=config.LOG_MAX_TRACEBACK_LENGTH)}")
                            continue

                    if config['access'] == 'r':
                        try:
                            with open(path, 'r') as _:
                                _data = _.read()

                            result_dict[file] = True

                        except PermissionError:
                            self._log(f"Failed to open file \"{path}\" for reading")
                            self._log(f"{format_exc(limit=config.LOG_MAX_TRACEBACK_LENGTH)}")
                            continue

        if all(result_dict.values()):
            return True

        return False

    def _check_networking(self) -> bool:
        connection_dict = {
            'database': {
                'host': config.AGENT.sql_server,
                'port': config.AGENT.sql_port,
            }
        }

        result_dict = {}

        for connection, settings in connection_dict.items():
            result, error = test_tcp_stream(host=settings['host'], port=settings['port'], out_error=True)

            if error is not None:
                self._log(f"Error while testing connection to {connection} (\"host: '{settings['host']}', port '{settings['port']}'\")")

            result_dict[connection] = result

        if all(result_dict.values()):
            return True

        return False

    def _check_database(self) -> bool:
        from core.config.db.check import Go as DBCheck

        db_connection_data_dict = {
            'server': config.AGENT.sql_server,
            'port': config.AGENT.sql_port,
            'user': config.AGENT.sql_user,
            'secret': config.AGENT.sql_secret,
            'database': config.AGENT.sql_database
        }

        try:
            return DBCheck(db_connection_data_dict).get()

        except ConnectionError as error:
            self._log(f"Error while testing database connection (\"host: '{db_connection_data_dict['server']}', port '{db_connection_data_dict['port']}'"
                      f"\"): \"{error}\"")
            self._log(f"{format_exc(limit=config.LOG_MAX_TRACEBACK_LENGTH)}")
            return False

    def _error(self, msg: str):
        self._log(msg)
        raise SystemError(msg)

    def _log(self, output, level: int = 1):
        if self.logger is not None:
            if len(self.log_cache) > 0:
                from core.utils.debug import log
                for _log in self.log_cache:
                    log(output=_log['output'], level=_log['level'])

                self.log_cache = []

            self.logger.write(output, level=level)

        else:
            self.log_cache.append({'level': level, 'output': output})

            if level == 1:
                journal.send(output)

    def _check_factory(self) -> bool:
        # REALLY basic check for errors

        from core.factory.main import get as factory

        try:
            self.CONFIG, self.current_config_dict = factory()

            if len(self.CONFIG) > 0:
                return True

        except Exception as error:
            self._log(f"An error occurred while processing factory: \"{error}\"")
            self._log(f"{format_exc(limit=config.LOG_MAX_TRACEBACK_LENGTH)}")

        return False


Prepare().start()
