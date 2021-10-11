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

# ga_version 0.9

# environmental variable PYTHONPATH must be set to the growautomation root-path for imports to work
#   (export PYTHONPATH=/var/lib/ga)
#   it's being set automatically by the systemd service

from core.config import shared_init_prestart as startup_shared_vars
startup_shared_vars.init()

from core.utils.threader import Loop as Thread
from core.factory.main import get as factory
from core.factory.reload import Go as Reload
from core.service.timer import get as get_timer
from core.config import shared as config
from core.utils.debug import fns_log
from core.service.decision import start as decision
from core.config.object.data.file import GaDataFile
from core.factory import config as factory_config

from time import sleep as time_sleep
from time import time
from os import getpid as os_getpid
from sys import exc_info as sys_exc_info
import signal


class Service:
    def __init__(self):
        self.exit_count = 0
        self.stop_count = 0
        signal.signal(signal.SIGUSR1, self.reload)
        signal.signal(signal.SIGTERM, self.hard_exit)
        signal.signal(signal.SIGINT, self.stop)
        self.CONFIG, self.current_config_dict = factory()
        self._init_shared_vars()
        self.timer_list = get_timer(config_dict=self.CONFIG)
        self.CONFIG_FILE = GaDataFile()
        self._update_config_file()
        self.THREADER = Thread()

    def start(self):
        try:
            fns_log(f"Service has process id {os_getpid()}", level=7)

            for instance in self.timer_list:
                self._thread(instance=instance)

            self.THREADER.start()
            fns_log('Start - finished starting threads.')
            self._status()

        except TypeError as error_msg:
            fns_log(f"Service encountered an error while starting:\n\"{error_msg}\"")
            self.stop()

        self._run()

    def reload(self, signum=None, stack=None):
        fns_log(f"Service received signal {signum}", level=3)
        fns_log('Service reload -> checking for config changes', level=4)

        # check current db config against currently loaded config
        reload, self.CONFIG, self.current_config_dict = Reload(
            object_list=self.CONFIG,
            config_dict=self.current_config_dict
        ).get()

        config.CONFIG = self.CONFIG

        if reload:
            fns_log('Reload - config has changed. Restarting threads.')
            # update shared config
            self._update_config_file()
            self._init_shared_vars()
            # re-create the list of possible timers
            self.timer_list = get_timer(config_dict=self.CONFIG)
            # stop and reset all current threads
            self.THREADER.stop()
            self.THREADER.jobs = []
            self._wait(seconds=config.SVC_WAIT_TIME)
            # re-create all the threads
            self.start()

        else:
            fns_log('Reload - config is up-to-date.')
            self._run()

    def stop(self, signum=None, stack=None):
        if self.stop_count >= config.SVC_MAX_STOP_COUNT:
            self.hard_exit(signum=signum)

        else:
            self.stop_count += 1
            fns_log('Service is stopping', level=6)
            fns_log('Stopping service.')
            self._signum_log(signum=signum)
            fns_log('Stopping timer threads', level=6)
            self.THREADER.stop()
            self._wait(seconds=config.SVC_WAIT_TIME)
            fns_log('Service stopped.')
            self._exit()

    def hard_exit(self, signum=None, stack=None):
        self._signum_log(signum)

        if self.stop_count >= config.SVC_MAX_STOP_COUNT:
            fns_log(f"Hard exiting service since it was stopped more than {config.SVC_MAX_STOP_COUNT} times", level=6)

        fns_log('Stopping service merciless', level=3)
        fns_log('Service stopped.')

        raise SystemExit('Service exited merciless!')

    def _init_shared_vars(self):
        config.init()
        config.CONFIG = self.CONFIG
        config.SYSTEM = self.CONFIG[factory_config.KEY_OBJECT_CONTROLLER][0]

    def _update_config_file(self):
        self.CONFIG_FILE.update()

    def _thread(self, instance):
        @self.THREADER.thread(
            sleep_time=int(instance.timer),
            thread_data=instance,
            description=instance.name,
        )
        def thread_task(data):
            decision(instance=data)

    @staticmethod
    def _wait(seconds: int):
        start_time = time()

        while time() < start_time + seconds:
            time_sleep(1)

    def _exit(self) -> None:
        if self.exit_count == 0:
            self.exit_count += 1
            fns_log('GrowAutomation service: Farewell!')

        raise SystemExit('Service exited gracefully.')

    @staticmethod
    def _signum_log(signum):
        if signum is not None:
            try:
                fns_log(f"Service received signal {signum} \"{sys_exc_info()[0].__name__}\"", level=3)

            except AttributeError:
                fns_log(f"Service received signal {signum}", level=3)

    def _status(self):
        thread_list = self.THREADER.list()
        detailed_thread_list = '\n'.join([str(thread.__dict__) for thread in thread_list])
        simple_thread_list = [thread.name for thread in thread_list]
        fns_log(f"Status - threads running: {simple_thread_list}")
        fns_log(f"Detailed info on running threads:\n{detailed_thread_list}", level=7)

    def _run(self):
        try:
            self._wait(seconds=config.SVC_WAIT_TIME)
            fns_log('Entering service runtime', level=7)
            run_last_reload_time = time()
            run_last_status_time = time()

            while True:
                if time() > (run_last_reload_time + config.SVC_RUN_RELOAD_INTERVAL):
                    self.reload()
                    break

                if time() > (run_last_status_time + config.SVC_RUN_STATUS_INTERVAL):
                    self._status()
                    run_last_status_time = time()

                time_sleep(config.SVC_RUN_LOOP_INTERVAL)

        except:
            try:
                error = sys_exc_info()[1]

                if str(error).find('Service exited') == -1:
                    fns_log(f"A fatal error occurred: \"{error}\"")

            except IndexError:
                pass

            if self.exit_count > 0:
                fns_log('Skipping service stop (gracefully) -> exiting (hard)', level=5)
                self._exit()

            else:
                self.stop()


Service().start()
