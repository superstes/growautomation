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

from re import match as regex_match
from os import listdir
from pathlib import Path
from subprocess import run as subprocess_run
from subprocess import DEVNULL
from json import loads as json_loads
from time import sleep


class Update:
    PROCESS_TIMEOUT = 300
    CMD_BACKUP_FILE = 'tar czf - %s | xz -7 > %s'
    CMD_BACKUP_SQL = 'mysqldump --defaults-file=%s --single-transaction --force %s | xz -7 > %s'
    NONE_RESULTS = ['', 'None', None, ' ']
    DB_CONFIG = 'database.cnf'
    BOOL_KEYS = ['FORCE']

    def __init__(self):
        apache_tmp_folder = [_dir for _dir in listdir('/tmp') if regex_match('systemd-private-.*-apache2.service.*', _dir) is not None][0]
        self.apache_tmp = f"/tmp/{apache_tmp_folder}"
        self.config_file = f"{self.apache_tmp}/tmp/ga_update.conf"
        self.config = {}
        self.path_update = None

    def start(self):
        if self._execute():
            print("Update succeeded! Exiting.")

        else:
            print("Update failed! Exiting.")

    def _execute(self):
        with open(self.config_file, 'r') as file:
            for line in file.readlines():
                _key, _value = line.split('=')
                key = _key.strip()
                value = _value.replace('\n', '').strip()
                if key in self.BOOL_KEYS:
                    self.config[key] = json_loads(value.lower())

                else:
                    self.config[key] = value

        self.path_update = f"{self.apache_tmp}{self.config['PATH_UPDATE']}"

        if self._backup():
            print('Successfully created backups!')

        else:
            print('Backup creation failed!')
            if self.config['FORCE']:
                print('Update is forced => continuing!')

            else:
                return False

        return True

    def _backup(self) -> bool:
        results = []
        Path(self.config['PATH_BACKUP']).mkdir(parents=True, exist_ok=True)

        print("Backing-up directories")
        sleep(3)
        results.append(self._process(cmd=self.CMD_BACKUP_FILE % (self.config['PATH_CORE'], f"{self.config['PATH_BACKUP']}/core.tar.xz")))
        results.append(self._process(cmd=self.CMD_BACKUP_FILE % (self.config['PATH_WEB'], f"{self.config['PATH_BACKUP']}/web.tar.xz")))
        results.append(self._process(cmd=self.CMD_BACKUP_FILE % (self.config['PATH_WEB_STATIC'], f"{self.config['PATH_BACKUP']}/web_static.tar.xz")))
        results.append(self._process(cmd=self.CMD_BACKUP_FILE % (self.config['PATH_HOME_CORE'], f"{self.config['PATH_BACKUP']}/home_core.tar.xz")))
        results.append(self._process(cmd=self.CMD_BACKUP_FILE % (self.config['PATH_HOME_WEB'], f"{self.config['PATH_BACKUP']}/home_web.tar.xz")))
        results.append(self._process(cmd=self.CMD_BACKUP_FILE % (self.config['PATH_LOG'], f"{self.config['PATH_BACKUP']}/log.tar.xz")))

        print("Backing-up database")
        sleep(3)
        results.append(self._process(cmd=self.CMD_BACKUP_SQL % (
            f"{self.config['PATH_WEB']}/{self.DB_CONFIG}",
            self.config['SQL_DB'],
            f"{self.config['PATH_BACKUP']}/db.sql.xz"
        )))

        sleep(3)
        print(f"Got backup files in {self.config['PATH_BACKUP']}: {listdir(self.config['PATH_BACKUP'])}")

        return all(results)

    def _process(self, cmd: str) -> bool:
        proc = subprocess_run(cmd, shell=True, timeout=self.PROCESS_TIMEOUT, stdout=DEVNULL)
        exit_code = proc.returncode

        if exit_code != 0:
            print(f"Subprocess for command '{cmd}' returned an error!")
            return False

        return True


if __name__ == '__main__':
    Update().start()
