#!/usr/bin/python3
# This file is part of Growautomation
#     Copyright (C) 2020  René Pascal Rath
#
#     Growautomation is free software: you can redistribute it and/or modify
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
#     Web: https://git.growautomation.at

# ga_version 0.7

from core.utils.connectivity import test_tcp_stream
from core.config import startup_shared as startup_shared_vars
from core.config import shared as shared_vars

from systemd import journal as systemd_journal
from sys import exc_info as sys_exc_info
from os import path as os_path
from os import stat as os_stat
from os import getuid as os_getuid
from os import getgid as os_getgid
from pathlib import Path
import signal


class Prepare:
    def __init__(self):
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT, self._stop)
        signal.signal(signal.SIGUSR1, self._stop)
        self.debug = False
        self.logger = None

    def start(self):
        self._log('Starting service initialization.')

        if self._check_file():
            startup_shared_vars.init()
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
            self._error('File check failed! Unable to start service!!')

    def _stop(self, signum=None, stack=None):
        if signum is not None:
            try:
                self._log("Service received signal %s - \"%s\"" % (signum, sys_exc_info()[0].__name__), level=3)
            except AttributeError:
                self._log("Service received signal %s" % signum, level=3)

        self._log('Service stopped.')

    def _check_file(self) -> bool:
        ga_uid = os_getuid()
        ga_gid = os_getgid()

        service_dir = Path(__file__).parent.absolute()
        subtract_to_root = 2  # how many dirs are it to get from here down to the ga root path
        ga_root_path = '/'.join(str(service_dir).split('/')[:-subtract_to_root])
        test_line = '##### FILE_TEST ####'

        file_dict = {
            'config': {
                'path': '/core/config/file/core.conf',
                'type': 'text',
                'access': 'rw',
                'perms': 600,
                'owner': ga_uid,
                'group': ga_gid,
            },
            'secret': {
                'path': '/core/secret/random.key',
                'type': 'text',
                'access': 'r',
                'perms': 400,
                'owner': ga_uid,
                'group': ga_gid,
            }
        }

        result_dict = {}

        for file, config in file_dict.items():
            full_path = "%s%s" % (ga_root_path, config['path'])
            result_dict[file] = False

            if os_path.exists(full_path):
                perms = int(oct(os_stat(full_path).st_mode)[-3:])
                owner = os_stat(full_path).st_uid
                group = os_stat(full_path).st_gid

                if perms != config['perms'] or owner != config['owner'] or group != config['group']:
                    self._log("Permissions for file \"%s\" are not set as expected" % full_path)
                    self._log("Permissions for file \"%s\" are \"owner '%s', group '%s', perms '%s'\" but should be \"owner '%s', group '%s', perms '%s'\""
                              % (full_path, owner, group, perms, config['owner'], config['group'], config['perms']), level=6)

                    # extended check
                    owner_perm = int(str(perms)[0])
                    group_perm = int(str(perms)[1])
                    other_perm = int(str(perms)[2])

                    if config['access'] == 'rw':
                        target_perm = 6
                    else:
                        target_perm = 4

                    sub_check_dict = {'owner': False, 'group': False}

                    if owner == config['owner'] or owner_perm >= target_perm:
                        sub_check_dict['owner'] = True

                    if owner == config['group'] or group_perm >= target_perm:
                        sub_check_dict['group'] = True

                    if other_perm >= target_perm:
                        sub_check_dict['other'] = True

                    if any(sub_check_dict.values()):
                        result_dict[file] = True

                    # log info

                if 'type' in config and config['type'] == 'text':
                    if config['access'] == 'rw':
                        try:
                            with open(full_path, 'r+') as _:
                                _data = _.read()

                            result_dict[file] = True

                        except PermissionError:
                            self._log("Failed to open file \"%s\" for writing" % full_path)
                            continue

                    if config['access'] == 'r':
                        try:
                            with open(full_path, 'r') as _:
                                _data = _.read()

                            result_dict[file] = True

                        except PermissionError:
                            self._log("Failed to open file \"%s\" for reading" % full_path)
                            continue

        if all(result_dict.values()):
            return True

        return False

    def _check_networking(self) -> bool:
        connection_dict = {
            'database': {
                'host': shared_vars.SYSTEM.sql_server,
                'port': shared_vars.SYSTEM.sql_port,
            }
        }

        result_dict = {}

        for connection, config in connection_dict.items():
            result, error = test_tcp_stream(host=config['host'], port=config['port'], out_error=True)

            if error is not None:
                self._log("Error while testing connection to %s (\"host: '%s', port '%s'\")" % (connection, config['host'], config['port']))

            result_dict[connection] = result

        if all(result_dict.values()):
            return True

        return False

    def _check_database(self) -> bool:
        from core.config.db.check import Go as DBCheck

        db_connection_data_dict = {
            'server': shared_vars.SYSTEM.sql_server,
            'port': shared_vars.SYSTEM.sql_port,
            'user': shared_vars.SYSTEM.sql_user,
            'secret': shared_vars.SYSTEM.sql_secret,
            'database': shared_vars.SYSTEM.sql_database
        }

        try:
            return DBCheck(db_connection_data_dict).get()

        except ConnectionError as error:
            self._log("Error while testing database connection (\"host: '%s', port '%s'\"): \"%s\""
                      % (db_connection_data_dict['server'], db_connection_data_dict['port'], error))
            return False

    def _error(self, msg: str):
        self._log(msg)
        raise SystemError(msg)

    def _log(self, output, level: int = 1):
        if self.logger is not None:
            self.logger.write(output, level=level)

        else:
            if level == 1:
                systemd_journal.write(output)

    def _check_factory(self) -> bool:
        # REALLY basic check for errors

        from core.factory.main import get as factory

        try:
            self.CONFIG, self.current_config_dict = factory()

            if len(self.CONFIG) > 0:
                return True

        except:
            error = sys_exc_info()[0]
            self._log("An error occurred while processing factory: \"%s\"" % error)

        return False


Prepare().start()
