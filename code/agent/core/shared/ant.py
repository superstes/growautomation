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

# provides functions/classes that are used throughout the project (and need other core modules like owl or config)

try:
    from core.config import Config
except (ImportError, ModuleNotFoundError):
    from config import Config
import smallant

from os import system as os_system


# File operations
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
