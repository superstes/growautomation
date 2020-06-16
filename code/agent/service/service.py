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

from threader import Loop
from worker import process as worker_process
from core.config import Config
from core.shared.shell import Output as ShellOutput
from core.shared.ant import debugger
from core.shared.varhandler import VarHandler
from core.shared.smallant import Log

from systemd import journal as systemd_journal
from time import sleep as time_sleep
from time import perf_counter as time_counter
from sys import argv as sys_argv
from os import getpid as os_getpid
from sys import exc_info as sys_exc_info

import signal

Threader = Loop()


class Service:
    def __init__(self):
        self.name_dict, self.init_exit, self.exit_count = {}, False, 0
        signal.signal(signal.SIGUSR1, self.reload)
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)

    def _get_timer_dict(self):
        name_dict = {}
        core_list = Config(output='name', table='object', filter="type = 'core'", exit=False).get('list')
        profile_list = Config(output='name', table='grp', filter="type = 'profile'", exit=False).get('list')
        sensor_type_list = Config(output='name', table='object', filter="class = 'sensor'", exit=False).get('list')
        function_sensor = Config(setting='function', belonging='sensor_master', exit=False).get('str')
        function_check = Config(setting='function', belonging='check', exit=False).get('str')
        function_path = Config(setting='path_root').get('str') + "/core/%s"

        debugger("service - timer |vars function_path '%s' |core_list '%s' |sensor_type_list '%s'"
                 % (function_path, core_list, sensor_type_list))
        # need to rewrite to check GrpSetting table for timers
        for timer_setting in Config(setting='timer', output="belonging,data", exit=False, distributed=True).get('list'):
            name, timer = timer_setting[0], timer_setting[1]
            if name in core_list or Config(setting='enabled', belonging=name, exit=False, distributed=True).get('int') == 1:
                if name in core_list:
                    name_dict["core_%s" % name] = {'timer': timer, 'function': function_path
                                                   % Config(setting='function', belonging=name, exit=False).get('str')}
                elif name in profile_list:
                    name_dict["profile_%s" % name] = {'timer': timer, 'function': function_path % function_check}
                else:
                    if name in sensor_type_list: devicetype = name
                    else: devicetype = Config(output='class', table='object', setting=name, exit=False).get('str')
                    if devicetype in sensor_type_list:
                        if Config(setting='enabled', belonging=devicetype, exit=False).get('int') == 1:
                            if name is False or timer is False:
                                debugger("service - timer |removed thread because of bad sql output")
                                continue
                            name_dict["sensor_%s" % name] = {'timer': timer, 'function': function_path % function_sensor}
                        else: continue
                    else: continue
            else: continue
            debugger("service - timer |dict '%s' '%s'" % (type(name_dict), name_dict))
        return name_dict

    def start(self):
        VarHandler(name='service_init', data=1).set()
        VarHandler(name='service_stop', data=0).set()
        try:
            if sys_argv[1] == 'debug': VarHandler(name='debug', data=1).set()
        except (IndexError, NameError): pass
        try:
            debugger("service - start |starting pid %s" % os_getpid())
            self.name_dict = self._get_timer_dict()
            for thread_name, setting in self.name_dict.items():
                setting_dict = dict(setting)
                interval, function = setting_dict['timer'], setting_dict['function']
                debugger("service - start |function '%s' '%s', interval '%s' '%s'"
                         % (type(function), function, type(interval), interval))

                @Threader.thread(int(interval), thread_name)
                def thread_process(initiator, start=False):
                    worker_process(initiator, start)

            Threader.start()
            systemd_journal.write('Finished starting service.')
            self._status()
        except TypeError as error:
            debugger("service - start |encountered error '%s'" % error)
            Log("Service encountered an error while starting:\n'%s'" % error).write()
            self.stop()
        self._run()

    def reload(self, signum=None, stack=None):
        debugger('service - reload |reloading config')
        name_dict_overwrite, reloaded_dict = {}, {}
        for reload_thread_name, reload_setting in self._get_timer_dict().items():
            reload_setting_dict = dict(reload_setting)
            reload_interval, reload_function = reload_setting_dict['timer'], reload_setting_dict['function']
            if reload_thread_name in self.name_dict:
                current_thread_dict = {key: value for key, value in self.name_dict.items() if key == reload_thread_name}
                current_thread_name = list(current_thread_dict.keys())[0]
                current_setting_dict = list(current_thread_dict.values())[0]
                current_interval, current_function = current_setting_dict['timer'], current_setting_dict['function']
                if reload_interval != current_interval:
                    name_dict_overwrite[reload_thread_name] = {'timer': reload_interval, 'function': reload_function}
                    reloaded_dict = [reload_interval, reload_function]
                    Threader.reload_thread(int(reload_interval), reload_thread_name)
                else: name_dict_overwrite[current_thread_name] = {'timer':current_interval, 'function': current_interval}
            else:
                name_dict_overwrite[reload_thread_name] = {'timer': reload_interval, 'function': reload_function}
                reloaded_dict = [reload_interval, reload_function]
                Threader.start_thread(int(reload_interval), reload_thread_name)
        debugger("service - reload |overwrite_dict '%s' '%s'" % (type(name_dict_overwrite), name_dict_overwrite))
        if len(reloaded_dict) > 0: systemd_journal.write("Updated configuration:\n%s" % reloaded_dict)
        self.name_dict = name_dict_overwrite
        systemd_journal.write('Finished configuration reload.')
        self._status()

    def _wait_timer(self, time: int, interval=5):
        count, start_time = 0, time_counter()
        while True:
            if count >= time:
                return True
            elif count % interval == 0:
                debugger("service - wait_timer |waited for %.2f seconds" % (time_counter() - start_time))
            time_sleep(1)
            count += 1

    def stop(self, signum=None, stack=None):
        debugger('service - stop |stopping')
        Log('Stopping service', level=1).write()
        systemd_journal.write('Stopping service.')
        if signum is not None:
            try:
                debugger("service - stop |got signal %s - '%s'" % (signum, sys_exc_info()[0].__name__))
                Log("Service received signal %s - '%s'" % (signum, sys_exc_info()[0].__name__))
            except AttributeError:
                debugger("service - stop |got signal %s" % signum)
                Log("Service received signal %s" % signum)
        debugger('service - stop |stopping threads')
        Threader.stop()
        self._wait_timer(5)
        debugger('service - stop |setting process stop-var')
        VarHandler(name='service_stop', data=1).set()
        self._wait_timer(15)
        debugger('service - stop |cleaning memory vars + disabling debug output')
        VarHandler().stop()
        self.init_exit = True
        systemd_journal.write('Service stopped.')
        self._exit()

    def _exit(self):
        if self.exit_count == 0:
            self.exit_count += 1
            ShellOutput(font='line', symbol='#')
            print("\n\nGrowautomation Service: Farewell! It has been my honor to serve you.\n")
            systemd_journal.write('Growautomation Service: Farewell! It has been my honor to serve you.')
            ShellOutput(font='line', symbol='#')
        raise SystemExit

    def _status(self):
        debugger(['service - status |updating status', "service - status |threads '%s'" % Threader.list(),
                  "service - status |config '%s'" % self.name_dict])
        systemd_journal.write("Threads running:\n%s\nConfiguration:\n" % Threader.list())
        for thread_name, setting_dict in self.name_dict.items():
            _list = []
            for setting, data in dict(setting_dict).items():
                _list.append("'%s': '%s'" % (setting, data))
            systemd_journal.write("'%s' | %s\n" % (thread_name, ', '.join(_list)))

    def _run(self):
        debugger('service - run |entering runtime')
        try:
            while_count, tired_time, start_time = 0, 60, time_counter()
            while True:
                while_count += 1
                debugger("service - run |loop count %s, loop runtime %.2f, pid %s" % (while_count, (time_counter() - start_time), os_getpid()))
                if while_count == 1440:
                    self.reload()
                    while_count = 0
                if while_count % 30 == 0: self._status()
                time_sleep(tired_time)
        except:
            if self.init_exit is False:
                debugger('service - run |runtime error')
                Log('Stopping service because of runtime error', level=2).write()
                self.stop()
            else: self._exit()


Service().start()
