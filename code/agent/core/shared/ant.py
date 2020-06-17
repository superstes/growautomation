#!/usr/bin/python3.8
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

# provides functions/classes that are used throughout the project
#   (to prevent recursive imports)

try:
    from core.handlers.config import Config
    import core.shared.smallant
    from core.handlers.debug import debugger
except (ImportError, ModuleNotFoundError):
    from config import Config
    import smallant
    from debug import debugger

from os import system as os_system
from time import sleep as time_sleep


class Line:
    def __init__(self, action, search, replace='', backup=False, file='./core.conf'):
        self.file, self.backup, self.searchfor, self.action, self.replacewith = file, backup, search, action, replace
        self.backupfile = "%s_%s_%s.bak" % (file, smallant.date_year_month_day, smallant.time_hour_minute)
        self.backupdir = "%s/%s" % (Config('path_backup').get(), smallant.date_year)

    def __repr__(self):
        self.find() if self.action == 'find' else self.delete() if self.action == 'delete' else self.replace() if self.action == 'replace' else self.add() if self.action == 'add' else None

    def find(self):
        with open(self.file, 'r') as _:
            for line in _.readlines():
                return line if line.find(self.searchfor) != -1 else False

    def delete(self):
        os_system("sed -i%s '/%s/d' %s && mv %s %s %s" % (self.backupfile, self.searchfor, self.file, self.file, self.backupfile, self.backupdir)) if self.backup == 'yes' \
            else os_system("sed -i '/%s/d' %s" % (self.searchfor, self.file))

    def replace(self):
        os_system("sed -i%s 's/%s/%s/p' %s && mv %s %s %s" % (self.backupfile, self.searchfor, self.replacewith, self.file, self.file, self.backupfile, self.backupdir)) if self.backup == 'yes' \
            else os_system("sed -i 's/%s/%s/g' %s" % (self.searchfor, self.replacewith, self.file))

    def add(self):
        # insert after linenr / search = linenr
        os_system("sed -i%s '%s a %s' %s && mv %s %s %s" % (self.backupfile, self.searchfor, self.replacewith, self.file, self.file, self.backupfile, self.backupdir)) if self.backup == 'yes' \
            else os_system("sed -i '%s a %s' %s" % (self.searchfor, self.replacewith, self.file))


def internal_process(target, argument=None, stdout=True, debug=False):
    from multiprocessing import Process as MP_Process
    from multiprocessing import Queue as MP_Queue
    if debug: debugger(command="smallant - internal_process |input: '%s' '%s'" % (type(target), target.__name__), hard_debug=True)
    stdout_pipe = MP_Queue()
    if stdout is True: _process = MP_Process(target=target, args=(argument, stdout_pipe))
    else: _process = MP_Process(target=target, args=argument)
    _process.start()
    runtime_count, finished = 1, False
    while True:
        if not _process.is_alive():
            _process.join()
            if stdout is True:
                output = stdout_pipe.get()
                if debug: debugger(command="smallant - internal_process |output: '%s' '%s'" % (type(output), output), hard_debug=True)
                return output
            return True
        elif runtime_count > 5:
            _process.terminate()
            _process.join()
            if debug: debugger(command="smallant - internal_process |timeout - terminated", hard_debug=True)
            return False
        else: time_sleep(3)
        runtime_count += 1
