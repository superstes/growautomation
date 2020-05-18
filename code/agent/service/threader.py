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

# base code source: https://github.com/sankalpjonn/timeloop
# modified for use in ga

from ..core.smallant import Log
from ..core.smallant import debugger

from threading import Thread, Event
from time import sleep as time_sleep
from datetime import timedelta


class Job(Thread):
    def __init__(self, interval, execute, name, run_once=False):
        Thread.__init__(self)
        self.state_stop = Event()
        self.interval, self.execute, self.name, self.run_once = interval, execute, name, run_once

    def stop(self):
        debugger("threader - Thread(stop) |thread stopping '%s'" % self.name)
        self.state_stop.set()
        self.join()
        Log("Stopped thread '%s'" % self.name, level=3).write()

    def run(self):
        Log("Starting thread '%s'" % self.name, level=4).write()
        debugger("threader - Thread(run) |thread starting '%s'" % self.name)
        if self.run_once:
            self.execute()
            Loop.stop_thread(self.name)
        else:
            while not self.state_stop.wait(self.interval.total_seconds()):
                self.execute()
                if self.state_stop.isSet():
                    debugger("threader - Thread(run) |thread exiting '%s'" % self.name)
                    Log("Exiting thread '%s'" % self.name, level=4).write()
                    break


class Loop:
    def __init__(self):
        self.jobs = []

    def start(self, daemon=True, single_thread=None):
        Log("Starting threads in background", level=3).write()
        for job in self.jobs:
            if single_thread is not None:
                debugger("threader - start |starting thread '%s' '%s'" % (type(single_thread), single_thread))
                if job.name == single_thread:
                    job.daemon = daemon
                    job.start()
            else:
                debugger("threader - start |starting threads")
                job.daemon = daemon
                job.start()
        if not daemon: self._block_root_process()

    def thread(self, sleep_time: int, thread_name):
        debugger("threader - thread |adding job |'%s' '%s' |interval '%s' '%s'" % (type(thread_name), thread_name, type(sleep_time), sleep_time))

        def decorator(function):
            if sleep_time == 0:
                sleep_time_new = 600
                self.jobs.append(Job(timedelta(seconds=sleep_time_new), function, thread_name, run_once=True))
            else: self.jobs.append(Job(timedelta(seconds=sleep_time), function, thread_name))
            return function
        return decorator

    def _block_root_process(self):
        debugger("threader - block |running threads in foreground")
        Log("Starting threads in foreground", level=3).write()
        while True:
            try:
                time_sleep(1)
            except:
                self.stop()
                raise SystemExit

    def stop(self):
        debugger("threader - stop |stopping jobs")
        for job in self.jobs: job.stop()
        Log("All threads stopped. Exiting loop", level=2).write()

    def stop_thread(self, thread_name):
        debugger("threader - stop_thread |'%s' '%s'" % (type(thread_name), thread_name))
        to_process_list = self.jobs
        for job in to_process_list:
            if job.name == thread_name:
                job.stop()
                self.jobs.remove(job)
                Log("Thread %s stopped." % job.name, level=2).write()

    def start_thread(self, sleep_time: int, thread_name):
        debugger("threader - start_thread |'%s' '%s' |interval '%s' '%s'" % (type(thread_name), thread_name, type(sleep_time), sleep_time))
        self.thread(sleep_time, thread_name)
        self.start(single_thread=thread_name)

    def reload_thread(self, sleep_time: int, thread_name):
        debugger("threader - reload_thread |'%s' '%s' |interval '%s' '%s'" % (type(thread_name), thread_name, type(sleep_time), sleep_time))
        self.stop_thread(thread_name)
        self.start_thread(sleep_time, thread_name)

    def list(self):
        debugger("threader - list |returning thread list")
        job_name_list = []
        for job in self.jobs: job_name_list.append(job.name)
        return job_name_list
