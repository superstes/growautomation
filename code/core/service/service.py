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
from core.config.object.device.output import GaOutputDevice, GaOutputModel
from core.factory import config as factory_config

from time import sleep as time_sleep
from time import time
from os import getpid as os_getpid
from sys import exc_info as sys_exc_info
from traceback import format_exc
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
                # we'll check if any output devices are active => they shouldn't be at this point in time
                if self._reverse_outputs(instance=instance):
                    self.THREADER.start_thread(description=instance.name)
                    self.THREADER.stop_thread(description=instance.name)

            self._wait(seconds=config.SVC_WAIT_TIME)

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
        reload_needed, reload_threads, _new_config, _new_config_dict = Reload(
            object_list=self.CONFIG,
            config_dict=self.current_config_dict,
            timers=self.timer_list,
        ).get()

        if reload_needed:
            fns_log('Reload - config has changed. Updating threads.')
            # update shared config
            self.CONFIG = _new_config
            self.current_config_dict = _new_config_dict
            config.CONFIG = self.CONFIG
            self._update_config_file()
            self._init_shared_vars()

            for old_timer in reload_threads['remove']:
                self.THREADER.stop_thread(description=old_timer.name)

                if isinstance(old_timer, (GaOutputModel, GaOutputDevice)):
                    self._reverse_outputs(instance=old_timer)

                self.timer_list.remove(old_timer)
                del old_timer

            self._wait(seconds=config.SVC_WAIT_TIME)

            for new_timer in reload_threads['add']:
                self._thread(instance=new_timer)
                self.THREADER.start_thread(description=new_timer.name)
                self.timer_list.append(new_timer)

            fns_log('Reload - Done reloading.')
            self._status()

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
        config.AGENT = self.CONFIG[factory_config.KEY_OBJECT_AGENT][0]
        config.SERVER = self.CONFIG[factory_config.KEY_OBJECT_SERVER][0]

    def _update_config_file(self):
        self.CONFIG_FILE.update()

    def _reverse_outputs(self, instance) -> bool:
        # todo: pass reverse-data to the reversal-process => timed reversal could calculate the approx. remaining time to wait before reversing
        if isinstance(instance, GaOutputDevice):
            if instance.active:
                self._thread(instance=instance, timer=1, settings={'action': 'stop'})
                return True

        elif isinstance(instance, GaOutputModel):
            for output in instance.member_list:
                if output.active:
                    self._thread(instance=output, timer=1, settings={'action': 'stop'})
                    return True

        return False

    def _thread(self, instance, timer: int = None, once: bool = False, settings: dict = None):
        @self.THREADER.add_thread(
            sleep_time=int(instance.timer) if timer is None else timer,
            thread_data=instance,
            description=instance.name,
            once=once,
            daemon=True,
        )
        def thread_task(data):
            decision(instance=data, settings=settings)

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
                if time() > (run_last_reload_time + config.AGENT.svc_interval_reload):
                    self.reload()
                    break

                if time() > (run_last_status_time + config.AGENT.svc_interval_status):
                    self._status()
                    run_last_status_time = time()

                time_sleep(config.SVC_LOOP_INTERVAL)

        except:
            try:
                exc_type, error, _ = sys_exc_info()

                if str(error).find('Service exited') == -1:
                    fns_log(f"A fatal error occurred: \"{exc_type} - {error}\"")
                    fns_log(f"{format_exc(limit=config.LOG_MAX_TRACEBACK_LENGTH)}")

            except IndexError:
                pass

            if self.exit_count > 0:
                fns_log('Skipping service stop (gracefully) -> exiting (hard)', level=5)
                self._exit()

            else:
                self.stop()


Service().start()
