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

# ga_version0.3

from ga.core.config import GetConfig
from ga.core.ant import LogWrite
from ga.core.ant import ShellOutput
from ga.service.threader import Loop

from systemd import journal as systemd_journal
import signal
from time import sleep as time_sleep
from sys import argv as sys_argv
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe
from os import getpid as os_getpid

LogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), level=2)
Threader = Loop()


class Service:
    def __init__(self, custom_args=None, debug=False):
        self.debug = debug
        self.custom_args = custom_args
        self.name_dict = {}
        self.init_exit, self.exit_count = False, 0
        signal.signal(signal.SIGUSR1, self.reload)
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
        self.start()

    def get_timer_dict(self):
        name_dict, path_root, core_list, sensor_type_list = {}, self.get_config(setting="path_root"), self.get_config(output="name", table="object", filter="type = 'core'")[0], \
                                                       self.get_config(output="name", table="object", filter="class = 'sensor'")
        function_sensor_master, function_check = self.get_config(setting="function", belonging="sensor_master"), self.get_config(setting="function", belonging="check")
        if self.debug: print("service - timer |vars path_root", path_root, "|core_list", core_list, "|sensor_type_list", sensor_type_list)
        for timer_setting in self.get_config(setting="timer", output="belonging,data"):
            name, timer = timer_setting[0], timer_setting[1]
            if name in core_list or self.get_config(setting="enabled", belonging=name) == "1":
                if name not in core_list:
                    if name in sensor_type_list: devicetype = name
                    else: devicetype = self.get_config(output="class", table="object", setting=name)
                    if devicetype in sensor_type_list:
                        if self.get_config(setting="enabled", belonging=devicetype) == "1":
                            function = "%s/sensor/%s" % (path_root, function_sensor_master)
                            name_dict["check_%s" % name] = [self.get_config(setting="timer_check", belonging=name), function_check]
                        else: continue
                    else:
                        continue
                elif name in core_list: function = "%s/core/%s" % (path_root, self.get_config(setting="function", belonging=name))
                else: continue
                name_dict[name] = [timer, function]
            else: continue
            if self.debug: print("service - timer |dict:", type(name_dict), name_dict)
        return name_dict

    def start(self):
        if self.debug: print("service - start |starting", "|pid", os_getpid())
        self.name_dict = self.get_timer_dict()
        for thread_name, settings in self.name_dict.items():
            interval, function = settings[0], settings[1]
            if self.debug: print("service - start |function", type(function), function, "|interval", type(interval), interval)

            @Threader.thread(int(interval), thread_name, debug=self.debug)
            def thread_function():
                output, error = subprocess_popen(["/usr/bin/python3 %s %s %s" % (function, thread_name, self.debug)], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
                if error.decode("ascii") != "":
                    LogWrite("Errors when starting %s:\n%s" % (thread_name, error.decode("ascii").strip()), level=2)
                    if self.debug: print("service - function error for thread", thread_name, "|error", error.decode("ascii").strip())
                LogWrite("Output when starting %s:\n%s" % (thread_name, output.decode("ascii").strip()), level=4)
        Threader.start()
        systemd_journal.write("Finished starting service.")
        self.status()
        self.run()

    def reload(self, signum=None, stack=None):
        if self.debug: print("service - reload |reloading config")
        name_dict_overwrite, dict_reloaded = {}, {}
        for thread_name_reload, settings_reload in self.get_timer_dict().items():
            if thread_name_reload in self.name_dict.keys():
                for thread_name, settings in self.name_dict.items():
                    if thread_name_reload == thread_name:
                        interval_reload, function_reload = settings[0], settings[1]
                        interval, function = settings[0], settings[1]
                        if interval_reload != interval:
                            name_dict_overwrite[thread_name_reload], dict_reloaded = [interval_reload, function_reload], [interval_reload, function_reload]
                            Threader.reload_thread(int(interval_reload), thread_name_reload)
                        else: name_dict_overwrite[thread_name] = [interval, function]
        if self.debug: print("service - reload |overwrite_dict:", type(name_dict_overwrite), name_dict_overwrite)
        if len(dict_reloaded) > 0: systemd_journal.write("Updated configuration:\n%s" % dict_reloaded)
        self.name_dict = name_dict_overwrite
        systemd_journal.write("Finished configuration reload.")
        self.status()

    def stop(self, signum=None, stack=None):
        if self.debug: print("service - stop |stopping")
        LogWrite("Stopping service", level=1)
        systemd_journal.write("Stopping service.")
        if signum is not None:
            if self.debug: print("service - stop |got signal", signum)
            LogWrite("Service received signal %s" % signum, level=2)
        Threader.stop()
        time_sleep(10)
        self.init_exit = True
        systemd_journal.write("Service stopped.")
        self.exit()

    def exit(self):
        if self.exit_count == 0:
            self.exit_count += 1
            ShellOutput(font="line", symbol="#")
            print("\n\nGrowautomation Service: Farewell! It has been my honor to serve you.\n")
            systemd_journal.write("Growautomation Service: Farewell! It has been my honor to serve you.")
            ShellOutput(font="line", symbol="#")
        raise SystemExit

    def status(self):
        if self.debug: print("service - status |updating status")
        if self.debug: print("service - status |threads: %s |config: %s" % (Threader.list(), self.name_dict))
        systemd_journal.write("Threads running:\n%s\nConfiguration:\n%s" % (Threader.list(), self.name_dict))

    def run(self):
        if self.debug: print("service - run |entering runtime")
        try:
            while_count, tired_time = 0, 300
            while True:
                while_count += 1
                if self.debug: print("service - run |loop count", while_count, "|loop runtime", tired_time * (while_count - 1), "|pid", os_getpid())
                if while_count == 288:
                    self.reload()
                    while_count = 0
                if while_count % 6 == 0: self.status()
                time_sleep(tired_time)
        except:
            if self.init_exit is False:
                if self.debug: print("service - run |runtime error")
                LogWrite("Stopping service because of runtime error", level=2)
                self.stop()
            else: self.exit()

    def get_config(self, setting=None, nosql=False, output=None, belonging=None, filter=None, table=None):
        return GetConfig(setting=setting, nosql=nosql, output=output, belonging=belonging, filter=filter, table=table, debug=self.debug).start()


try:
    if sys_argv[1] is not None:
        Service(debug=True) if sys_argv[1] == "debug" else Service()
except IndexError: Service()
