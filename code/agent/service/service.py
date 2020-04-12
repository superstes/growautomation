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

from ga.service.threader import Loop

from systemd.daemon import notify as systemd_notify
from systemd.daemon import Notification as systemd_notification
from signal import signal, SIGTERM, SIGUSR1
from time import sleep
from sys import argv as sys_argv
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe

Threader = Loop()

LogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), level=2)


class Service:
    def __init__(self, custom_args=None, debug=False):
        self.debug = debug
        self.custom_args = custom_args
        self.name_dict = {}
        self.core_list = self.get_config(table="object", filter="type = 'core'")
        signal(SIGTERM, self.stop())
        signal(SIGUSR1, self.reload())
        self.start()

    def get_timer_dict(self):
        name_dict = {}
        path_root = self.get_config(setting="path_root")
        for row in self.get_config(setting="timer", output="belonging,data"):
            if row[0] in self.core_list or self.get_config(setting="enabled", belonging=row[0]) == "1":
                if self.get_config(output="type", table="object", setting=row[0]) is not "device": function = self.get_config(setting="function", belonging=row[0])
                else:
                    devicetype = self.get_config(output="class", table="object", setting=row[0])
                    if self.get_config(setting="enabled", belonging=devicetype) == "1":
                        function = self.get_config(setting="function", belonging=devicetype)
                    else: pass
                if row[0] in self.core_list: path_function = "%s/core/%s" % (path_root, function)
                else: path_function = "%s/sensor/%s" % (path_root, function)
                name_dict[row[0]] = [row[1], path_function]
            else: pass
            if self.debug: print(type(name_dict), name_dict)
        return name_dict

    def start(self):
        self.name_dict = self.get_timer_dict()
        for thread_name, settings in self.name_dict.items():
            interval, function = settings[0], settings[1]
            if self.debug: print("start function:", type(function), function, "interval:", type(interval), interval)

            @Threader.thread(interval, thread_name)
            def thread_function():
                output, error = subprocess_popen(["/usr/bin/python3 %s" % function], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
                if error.decode("ascii") != "": LogWrite("Errors when starting %s:\n%s" % (thread_name, error.decode("ascii").strip()), level=2)
                LogWrite("Output when starting %s:\n%s" % (thread_name, output.decode("ascii").strip()), level=4)
        Threader.start()
        self.status()
        systemd_notify(systemd_notification.READY)
        self.run()

    def reload(self):
        name_dict_overwrite = {}
        for thread_name_reload, settings_reload in self.get_timer_dict().items():
            if thread_name_reload in self.name_dict.keys():
                for thread_name, settings in self.name_dict.items():
                    if thread_name_reload == thread_name:
                        interval_reload, function_reload = settings[0], settings[1]
                        interval, function = settings[0], settings[1]
                        if interval_reload != interval:
                            name_dict_overwrite[thread_name_reload] = [interval_reload, function_reload]
                            Threader.reload_thread(interval_reload, thread_name_reload)
                        else: name_dict_overwrite[thread_name] = [interval, function]
        if self.debug: print("reload overwrite:", type(name_dict_overwrite), name_dict_overwrite)
        self.name_dict = name_dict_overwrite
        self.status()
        self.run()

    def stop(self):
        systemd_notify(systemd_notification.STOPPING)
        Threader.stop()
        sleep(10)
        self.status()
        raise SystemExit

    def status(self):
        systemd_notify(systemd_notification.STATUS, "Threads running:\n%s\n\nConfiguration:\n%s" % (Threader.list(), self.name_dict))

    def run(self):
        try:
            while_count = 0
            while True:
                if self.debug: print("run loop count:", while_count)
                if while_count == 287: self.reload()
                sleep(300)
                self.status()
                while_count += 1
        except Exception as error:
            if self.debug: print("run error:", error)
            LogWrite("Stopping service because of runtime error:\n%s" % error)
            self.stop()

    def get_config(self, setting=None, nosql=False, output=None, belonging=None, filter=None, table=None):
        return GetConfig(setting=setting, nosql=nosql, output=output, belonging=belonging, filter=filter, table=table, debug=self.debug)


try:
    if sys_argv[1] is not None:
        try:
            if sys_argv[2] is not None: Service(custom_args=sys_argv[2], debug=True) if sys_argv[1] == "debug" else Service()
        except IndexError: Service(debug=True) if sys_argv[1] == "debug" else Service()
    elif sys_argv[2] is not None:
        try: Service(custom_args=sys_argv[2])
        except IndexError: Service()
except IndexError: Service()
