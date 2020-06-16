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

from core.owl import DoSql
from core.shared.ant import debugger
from core.shared.varhandler import VarHandler
from core.config import Config
from core.shared.smallant import Log

from systemd import journal as systemd_journal
from sys import argv as sys_argv
from sys import exc_info as sys_exc_info
from os import system as os_system
import signal


class Prepare:
    def __init__(self):
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT, self._stop)
        self.debug = False

    def start(self):
        VarHandler(name='init', data=1).set()
        try:
            if sys_argv[1] == 'debug':
                VarHandler(name='debug', data=1).set()
                self.debug = True
        except (IndexError, NameError): pass
        systemd_journal.write('Starting service initialization.')
        self._var_cleanup()
        self._db_connection_test()
        self._config_update()
        self._finish()
        # recreate log/backup links
        # check python version -> for future dynamic python version usage

    def _stop(self, signum=None, stack=None):
        if signum is not None:
            try:
                debugger("earlybird - stop |got signal %s - '%s'" % (signum, sys_exc_info()[0].__name__))
                Log("Service initiation received signal %s - '%s'" % (signum, sys_exc_info()[0].__name__), level=2).write()
            except AttributeError:
                debugger("earlybird - stop |got signal %s" % signum)
                Log("Service initiation received signal %s" % signum, level=2).write()
        debugger('earlybird - stop |received error - exiting')
        systemd_journal.write('Service initiation initialization stopped. Exiting.')
        VarHandler().stop()

    def _finish(self):
        debugger('earlybird - finish |finished service preparations')
        systemd_journal.write('Finished service initialization.')
        VarHandler().stop()

    def _config_update(self):
        def update(file):
            file_dict, db_dict = {}, {}
            with open(file, 'r') as config_file:
                line_list = config_file.readlines()
                for line in line_list:
                    if line.find('=') != -1:
                        _ = line.split('=', 1)
                        file_dict[_[0]] = _[1].strip()
            for setting, file_data in file_dict.items():
                db_data = Config(setting=setting).get()
                if db_data is not False:
                    if db_data != file_data:
                        os_system("sed -i 's$%s$%s$g' %s" % ("%s=%s" % (setting, file_data), "%s=%s" % (setting, db_data), file))
                        debugger("earlybird - config_update |updated setting '%s' in file '%s'" % (setting, file))
                        Log("Updated setting '%s' data in config file '%s'" % (setting, file))
                else:
                    debugger("earlybird - config_update |setting '%s' not found in db" % setting)
                    continue
        update(file="%s/core/core.conf" % Config(setting='path_root').get())
        update(file='/etc/growautomation.version')

    def _db_connection_test(self):
        error = False
        if DoSql(test=True, exit=False).start() is False:
            debugger('earlybird - db |read - connection error')
            Log('Cannot read from growautomation database', level=1)
            error = True
        if DoSql(test=True, write=True, exit=False).start() is False:
            debugger('earlybird - db |write - connection error')
            Log('Cannot write to growautomation database', level=1)
            error = True
        if error:
            systemd_journal.write('Error while testing growautomation database connection')

    def _var_cleanup(self):
        def clean_if_exists(name):
            if VarHandler(name=name).get() is not False:
                VarHandler(name=name).clean()

        [clean_if_exists('lock_%s' % _) for _ in Config(output='name', table='object').get()]
        if not self.debug: clean_if_exists('debug')
        clean_if_exists('service_stop')


Prepare().start()
