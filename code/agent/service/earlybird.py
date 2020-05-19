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
#     E-Mail: rene.rath@growautomation.at
#     Web: https://git.growautomation.at

# ga_version 0.4

from ..core.owl import DoSql
from ..core.smallant import debugger
from ..core.smallant import VarHandler
from ..core.config import Config
from ..core.smallant import Log

from systemd import journal as systemd_journal
from sys import argv as sys_argv
from sys import exc_info as sys_exc_info
import signal


class Startup:
    def __init__(self):
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
#        self.start()
#        not finished yet

    def start(self):
        try:
            if sys_argv[1] == 'debug': VarHandler(name='debug', data=1).set()
        except (IndexError, NameError): pass
        systemd_journal('Starting service initialization.')
        # recreate log/backup links
        # check for python version -> module link should be updated

    def stop(self, signum=None, stack=None):
        if signum is not None:
            debugger("service - stop |got signal %s - '%s'" % (signum, sys_exc_info()[0].__name__))
            Log("Service received signal %s - '%s'" % (signum, sys_exc_info()[0].__name__), level=2).write()
        systemd_journal('Service initialization stopped. Exiting.')

    def finish(self):
        try:
            if sys_argv[1] == 'debug': VarHandler(name='debug').clean()
        except (IndexError, NameError): pass

    def config(self):
        return False
        # get config from db
        # check against locally written config files (core.conf/version file)

    def db(self):
        sql = DoSql()

        def db_read_test():
            data = sql.connect('SELECT * FROM ga.Setting ORDER BY changed DESC LIMIT 10;')
            result = True if type(data) == list else data if type(data) == bool else False
            return result

        def db_write_test():
            sql.connect("INSERT INTO ga.Setting (author, belonging, setting, data) VALUES ('owl', '%s', 'conntest', 'ok');" % Config('hostname').get())
            sql.connect("DELETE FROM ga.Setting WHERE author = 'owl' and belonging = '%s';" % Config('hostname').get())
            return True
        if db_read_test() is True and db_write_test() is True:
            DoSql('DELETE FROM ga.Temp;', write=True).start()
            # check that no locks are set -> set all to 0 or simply remove them (or remove all entries from temp table ?!)


Startup()
