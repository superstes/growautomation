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

from ga.core.config import Config
from ga.core.ant import LogWrite
from ga.core.ant import ShellOutput
from ga.service.threader import Loop
from ga.core.globalvars import init_vars
from ga.core.smallant import debugger

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
    def __init__(self):
        self.name_dict, self.init_exit, self.exit_count = {}, False, 0
        signal.signal(signal.SIGUSR1, self.reload)
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
        self.start()

    def get_timer_dict(self):
        name_dict = {}
        core_list = Config(output="name", table="object", filter="type = 'core'").get()[0]
        sensor_type_list = Config(output="name", table="object", filter="class = 'sensor'").get()
        function_sensor_master = Config(setting="function", belonging="sensor_master").get()
        function_check = Config(setting="function", belonging="check").get()
        function_path = Config(setting="path_root").get() + "/core/%s"
        debugger("service - timer |vars function_path '%s' |core_list '%s' |sensor_type_list '%s'" % (function_path, core_list, sensor_type_list))
        for timer_setting in Config(setting="timer", output="belonging,data").get():
            name, timer = timer_setting[0], timer_setting[1]
            if name in core_list or Config(setting="enabled", belonging=name).get() == "1":
                if name not in core_list:
                    if name in sensor_type_list: devicetype = name
                    else: devicetype = Config(output="class", table="object", setting=name).get()
                    if devicetype in sensor_type_list:
                        if Config(setting="enabled", belonging=devicetype).get() == "1":
                            function = function_sensor_master
                            name_dict["check_%s" % name] = [Config(setting="timer_check", belonging=name).get(), function_path % function_check]
                        else: continue
                    else: continue
                elif name in core_list: function = Config(setting="function", belonging=name).get()
                else: continue
                name_dict[name] = [timer, function_path % function]
            else: continue
            debugger("service - timer |dict '%s' '%s'" % (type(name_dict), name_dict))
        return name_dict

    def start(self):
        self.debug()
        debugger("service - start |starting |pid %s" % os_getpid())
        self.name_dict = self.get_timer_dict()
        for thread_name, settings in self.name_dict.items():
            interval, function = settings[0], settings[1]
            debugger("service - start |function '%s' '%s' |interval '%s' '%s'" % (type(function), function, type(interval), interval))

            @Threader.thread(int(interval), thread_name)
            def thread_function():
                LogWrite("Starting function '%s' for object %s." % (function, thread_name), level=4)
                output, error = subprocess_popen(["/usr/bin/python3 %s %s" % (function, thread_name)], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
                output_str, error_str = output.decode("ascii").strip(), error.decode("ascii").strip()
                if error_str != "":
                    LogWrite("Error by executing %s:\n'%s'" % (thread_name, error_str), level=2)
                    debugger("service - start | thread_function |error for thread '%s' '%s'" % (thread_name, error_str))
                LogWrite("Output by processing %s:\n'%s'" % (thread_name, output_str), level=3)
                debugger("service - start | thread_function |output by processing '%s' '%s'" % (thread_name, output_str))
        Threader.start()
        systemd_journal.write("Finished starting service.")
        self.status()
        self.run()

    def reload(self, signum=None, stack=None):
        debugger("service - reload |reloading config")
        name_dict_overwrite, dict_reloaded = {}, {}
        for thread_name_reload, settings_reload in self.get_timer_dict().items():
            interval_reload, function_reload = settings_reload[0], settings_reload[1]
            if thread_name_reload in self.name_dict.keys():
                for thread_name, settings in self.name_dict.items():
                    if thread_name_reload == thread_name:
                        interval, function = settings[0], settings[1]
                        if interval_reload != interval:
                            name_dict_overwrite[thread_name_reload], dict_reloaded = [interval_reload, function_reload], [interval_reload, function_reload]
                            Threader.reload_thread(int(interval_reload), thread_name_reload)
                        else: name_dict_overwrite[thread_name] = [interval, function]
            else:
                name_dict_overwrite[thread_name_reload], dict_reloaded = [interval_reload, function_reload], [interval_reload, function_reload]
                Threader.start_thread(int(interval_reload), thread_name_reload)
        debugger("service - reload |overwrite_dict '%s' '%s'" % (type(name_dict_overwrite), name_dict_overwrite))
        if len(dict_reloaded) > 0: systemd_journal.write("Updated configuration:\n%s" % dict_reloaded)
        self.name_dict = name_dict_overwrite
        systemd_journal.write("Finished configuration reload.")
        self.status()

    def stop(self, signum=None, stack=None):
        debugger("service - stop |stopping")
        LogWrite("Stopping service", level=1)
        systemd_journal.write("Stopping service.")
        if signum is not None:
            debugger("service - stop |got signal '%s'" % signum)
            LogWrite("Service received signal '%s'" % signum, level=2)
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
        debugger(["service - status |updating status", "service - status |threads '%s' |config '%s'" % (Threader.list(), self.name_dict)])
        systemd_journal.write("Threads running:\n%s\nConfiguration:\n%s" % (Threader.list(), self.name_dict))

    def run(self):
        debugger("service - run |entering runtime")
        try:
            while_count, tired_time = 0, 300
            while True:
                while_count += 1
                debugger("service - run |loop count %s |loop runtime %s |pid %s" % (while_count, tired_time * (while_count - 1), os_getpid()))
                if while_count == 288:
                    self.reload()
                    while_count = 0
                if while_count % 6 == 0: self.status()
                time_sleep(tired_time)
        except:
            if self.init_exit is False:
                debugger("service - run |runtime error")
                LogWrite("Stopping service because of runtime error", level=2)
                self.stop()
            else: self.exit()

    def debug(self):
        init_vars()
        from ga.core.globalvars import tmp_dict
        try:
            if sys_argv[1] == "debug": tmp_dict["debug"] = 1
            else: tmp_dict["debug"] = 0
        except (IndexError, NameError): pass


Service()
