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

# ga_version 0.6

# environmental variable PYTHONPATH must be set to the growautomation root-path for imports to work
#   (export PYTHONPATH=/etc/ga)
#   is being set automatically by the systemd service

from core.utils.threader import Loop as Thread
from core.config.object.factory.factory import Go as Factory
from core.config.object.factory.reload import Go as Reload
from core.service.timer import get as Timer
from core.config import shared as shared_vars
from core.utils.debug import debugger
from core.utils.debug import Log
from core.config.object.core.controller import GaControllerDevice
from core.service.decision import Go as Decision
from core.config.object.data.file import GaDataFile

from systemd import journal as systemd_journal
from time import sleep as time_sleep
from time import time
from os import getpid as os_getpid
from sys import exc_info as sys_exc_info
import signal


class Service:
    RUN_RELOAD_INTERVAL = 86400
    RUN_STATUS_INTERVAL = 1200
    RUN_LOOP_INTERVAL = 60
    MAX_STOP_COUNT = 3
    WAIT_TIME = 5

    def __init__(self):
        self.exit_count = 0
        self.stop_count = 0
        signal.signal(signal.SIGUSR1, self.reload)
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
        self.THREAD = Thread()
        self.CONFIG, self.current_config_dict = Factory().get()
        self.timer_list, self.custom_timer_list = Timer(config_dict=self.CONFIG)
        self.CONFIG_FILE = GaDataFile()
        self._init_shared_vars()
        self._update_config_file()
        self.LOG = Log()

    def start(self):
        try:
            debugger("service | start | process id %s" % os_getpid())

            for instance in self.timer_list:
                self._thread(instance=instance)

            self.THREAD.start()
            systemd_journal.write('Start - finished starting threads.')
            self._status()

        except TypeError as error_msg:
            debugger("service | start | encountered error '%s'" % error_msg)
            self.LOG.write(output="Service encountered an error while starting:\n'%s'" % error_msg)
            self.stop()
        self._run()

    def reload(self, signum=None, stack=None):
        debugger('service | reload | checking for config changes')
        # check current db config against currently loaded config
        reload, self.CONFIG, self.current_config_dict = Reload(
            object_list=self.CONFIG,
            config_dict=self.current_config_dict
        ).get()

        shared_vars.CONFIG = self.CONFIG

        if reload:
            debugger('service | reload | reloading threads tue to config changes')
            systemd_journal.write('Reload - config changed. Restarting threads.')
            # update shared config
            self._update_config_file()
            self._init_shared_vars()
            # re-create the list of possible timers
            self.timer_list, self.custom_timer_list = Timer(config_dict=self.CONFIG)
            # stop and reset all current threads
            self.THREAD.stop()
            self.THREAD.jobs = []
            self._wait(seconds=self.WAIT_TIME)
            # re-create all the threads
            self.start()
        else:
            debugger('service | reload | no config changes')
            systemd_journal.write('Reload - config is up-to-date.')
            self._run()

    def stop(self, signum=None, stack=None):
        if self.stop_count >= self.MAX_STOP_COUNT:
            self._hard_exit()
        self.stop_count += 1
        debugger('service | stop | stopping')
        self.LOG.write(output='Stopping service', level=1)
        systemd_journal.write('Stopping service.')
        if signum is not None:
            try:
                debugger("service | stop | got signal %s - '%s'" % (signum, sys_exc_info()[0].__name__))
                self.LOG.write(output="Service received signal %s - '%s'" % (signum, sys_exc_info()[0].__name__))
            except AttributeError:
                debugger("service | stop | got signal %s" % signum)
                self.LOG.write(output="Service received signal %s" % signum)
        debugger('service | stop | stopping threads')
        self.THREAD.stop()
        self._wait(seconds=self.WAIT_TIME)
        systemd_journal.write('Service stopped.')
        self._exit()

    def _init_shared_vars(self):
        shared_vars.init()
        shared_vars.CONFIG = self.CONFIG
        found = False

        for obj in self.CONFIG['object']:
            if isinstance(obj, GaControllerDevice):
                try:
                    if obj.name == self.CONFIG_FILE.get()['name']:
                        shared_vars.SYSTEM = obj
                        found = True
                        break
                except KeyError:
                    shared_vars.SYSTEM = obj
                    found = True
                    break

        if not found:
            debugger("service | _init_shared_vars | no acceptable system object found in list:\n'%s'" % self.CONFIG)
            systemd_journal.write("Init-shared-vars - no acceptable system object found:\n%s\n" % self.CONFIG)
            self._exit()

    def _update_config_file(self):
        self.CONFIG_FILE.update()

    def _thread(self, instance):
        @self.THREAD.thread(sleep_time=int(instance.timer), thread_instance=instance)
        def thread_task(thread_instance, start=False):
            Decision(instance=thread_instance).start()

    def _wait(self, seconds: int):
        start_time = time()
        while time() < start_time + seconds:
            time_sleep(1)

    def _exit(self) -> None:
        if self.exit_count == 0:
            self.exit_count += 1
            # ShellOutput(font='line', symbol='#')
            print("\n\nGrowautomation service: Farewell!\n")
            systemd_journal.write('Growautomation service: Farewell!')
            # ShellOutput(font='line', symbol='#')
        raise SystemExit('Service exited gracefully.')

    def _hard_exit(self):
        debugger("service | _hard_exit | hard exiting service sice it was stopped more than %s times"
                 % self.MAX_STOP_COUNT)
        self.LOG.write(output='Stopping service merciless', level=1)
        systemd_journal.write('Service stopped.')
        raise SystemExit('Service exited merciless!')

    def _status(self):
        thread_list = self.THREAD.list()
        detailed_thread_list = [str(thread.__dict__) for thread in thread_list]
        simple_thread_list = [thread.name for thread in thread_list]
        debugger("service | status | threads running:\n\n\n'%s'\n\n" % "\n\n".join(detailed_thread_list))
        systemd_journal.write("Status - threads running:\n%s\n" % simple_thread_list)

    def _run(self):
        try:
            debugger('service | run | starting runtime')
            run_last_reload_time = time()
            run_last_status_time = time()
            while True:
                if time() > run_last_reload_time + self.RUN_RELOAD_INTERVAL:
                    self.reload()
                    break
                if time() > run_last_status_time + self.RUN_STATUS_INTERVAL:
                    self._status()
                    run_last_status_time = time()
                time_sleep(self.RUN_LOOP_INTERVAL)
        except:
            if self.exit_count > 0:
                debugger("service | _run | skipping stop -> exiting")
                self._exit()
            else:
                self.stop()


Service().start()
