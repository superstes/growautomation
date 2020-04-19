#!/usr/bin/python
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

# ga_version 0.3

from ga.core.owl import DoSql
from ga.core.owl import debugger
from ga.core.owl import sql_replace
from ga.core.config import Config
from ga.core.smallant import LogWrite

from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe
import signal
from systemd import journal as systemd_journal
from sys import argv as sys_argv

LogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), level=2)


class Startup:
    def __init__(self):
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
        self.start()

    def start(self):
        systemd_journal("Starting service initialization.")
        # recreate log/backup links
        # check for python version -> module link should be updated

    def stop(self, signum=None, stack=None):
        self.debug(cleanup=True)
        if signum is not None:
            debugger("service - stop |got signal '%s'" % signum)
            LogWrite("Service received signal '%s'" % signum, level=2)
        systemd_journal("Service initialization stopped. Exiting.")

    def config(self):
        # get config from db
        # check against locally written config files (core.conf/version file)

    def db(self):
        sql = DoSql()
        def db_read_test():
            data = sql.connect("SELECT * FROM ga.Setting ORDER BY changed DESC LIMIT 10;")
            result = True if type(data) == list else data if type(data) == bool else False
            return result
        def db_write_test():
            sql.connect("INSERT INTO ga.Setting (author, belonging, setting, data) VALUES ('owl', '%s', 'conntest', 'ok');" % Config("hostname").get())
            sql.connect("DELETE FROM ga.Setting WHERE author = 'owl' and belonging = '%s';" % Config("hostname").get())
            data = True
        if db_read_test() is True and db_write_test() is True:
            DoSql("DELETE FROM ga.Temp;", write=True).start()
            # check that no locks are set -> set all to 0 or simply remove them (or remove all entries from temp table ?!)

    def debug(self, cleanup=False):
        data_dict = {"data": None, "author": "service", "belonging": Config("hostname").get(), "setting": "debug"}
        if cleanup:
            data_dict["data"] = "0"
            sql_replace(data_dict, table="tmp")
        else:
            try:
                if sys_argv[1] == "debug":
                    data_dict["data"] = "1"
                    sql_replace(data_dict, table="tmp", debug=True)
                else:
                    data_dict["data"] = "0"
                    sql_replace(data_dict, table="tmp")
            except IndexError: pass

Startup()
