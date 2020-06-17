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

# ga_version 0.5

from core.handlers.config import Config
from core.handlers.debug import Log
from core.shared.smallant import now
from core.handlers.debug import debugger
from core.shared.smallant import process

from os import path as os_path


class Backup:
    def __init__(self):
        self.hostname = Config(setting='hostname').get()
        self.backup_path = Config(setting='path_backup', belonging=self.hostname).get()

    def start(self):
        if self._check() is True:
            return self._work()
        else:
            debugger('backup - start |check failed - exiting')
            Log('Backup check failed - exiting').write()

    def _check(self):
        enabled, mount, path = False, False, False
        if Config(setting='enabled', belonging='backup').get('int') == 1 and Config(setting='backup', belonging=self.hostname).get('int') == 1:
            debugger('backup - check |backup is enabled')
            enabled = True
            if Config(setting='mnt_backup', belonging=self.hostname).get('int') == 0:
                debugger('backup - check |no backup mount to check')
                mount = True
            else:
                mount_type, current_mounts = Config(setting='mnt_backup_type', belonging=self.hostname).get(), process('mount -l')
                if current_mounts.find(mount_type) != -1:
                    if current_mounts.find(Config(setting='mnt_backup_share', belonging=self.hostname).get()) != -1:
                        debugger('backup - check |backup mount verified')
                        mount = True
                debugger('backup - check |backup mount verification error')
                Log('Backup mount could not be verified', level=2).write()
            if os_path.exists(self.backup_path) is True:
                path = True
            else:
                debugger('backup - check |backup path does not exist')
                Log("Backup path '%s' does not exist" % self.backup_path, level=2).write()
        else:
            debugger('backup - check |backup is disabled')
            Log('Backup is disabled', level=2).write()

        if not enabled or not mount or not path:
            return False
        else: return True

    def _work(self):
        work_status_list = []
        backup_dir = "%s/%s/%s" % (self.backup_path, now("%Y"), now("%m"))
        tmp_dir = "/tmp/%s_growautomation_backup" % (now("%Y_%m_%d-%H_%M_%S"))
        debugger('backup - work |copying code to tmp dir')

        def task(command, debug_output):
            debugger("backup - work |%s" % debug_output)
            output, error = process(command, out_error=True)
            if error is not None and error != '':
                debugger("backup - work |error while %s: '%s'" % (debug_output, error))
                Log("Backup error while copying root directory:\n'%s'" % error, level=1)
                return True
            return False

        work_status_list.append(task(command="mkdir -p %s & mkdir -p %s" % (tmp_dir, backup_dir), debug_output='creating directories'))
        work_status_list.append(task(command="cp -r %s %s" % (Config(setting='path_root', belonging=self.hostname).get(), tmp_dir),
                                     debug_output='copying root directory'))
        work_status_list.append(task(command="mysqldump ga > %s/ga.mysqldump" % tmp_dir, debug_output='dumping database'))
        work_status_list.append(task(command="tar -czvf %s/%s_backup.tar.gz -C /tmp ./%s" % (backup_dir, now("%d_%H-%M-%S"), tmp_dir[4:]),
                                     debug_output='compressing backup'))
        work_status_list.append(task(command="rm -rf %s" % tmp_dir, debug_output='cleaning temporary files'))
        return False if any(work_status_list) is False else True


if __name__ == '__main__':
    Backup.start(Backup())
