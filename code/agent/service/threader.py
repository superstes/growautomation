# source: https://github.com/sankalpjonn/timeloop
# modified for use in ga

# ga_version 0.3

from ga.core.ant import LogWrite
from ga.core.owl import debugger

from threading import Thread, Event
from time import sleep as time_sleep
from datetime import timedelta
from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe

LogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), level=2)


class Job(Thread):
    def __init__(self, interval, execute, name, run_once=False):
        Thread.__init__(self)
        self.state_stop = Event()
        self.interval = interval
        self.execute = execute
        self.name = name
        self.run_once = run_once

    def stop(self):
        debugger("threader - Thread(stop) |thread stopping '%s'" % self.name)
        self.state_stop.set()
        self.join()
        LogWrite("Stopped thread '%s'" % self.name, level=3)

    def run(self):
        LogWrite("Starting thread '%s'" % self.name, level=4)
        debugger("threader - Thread(run) |thread starting '%s'" % self.name)
        if self.run_once:
            self.execute()
            Loop.stop_thread(self.name)
        else:
            while not self.state_stop.wait(self.interval.total_seconds()):
                self.execute()
                if self.state_stop.isSet():
                    debugger("threader - Thread(run) |thread exiting '%s'" % self.name)
                    LogWrite("Exiting thread '%s'" % self.name, level=4)
                    break


class Loop:
    def __init__(self):
        self.jobs = []

    def start(self, daemon=True, single_thread=None):
        LogWrite("Starting threads in background", level=3)
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
        if not daemon: self.block_root_process()

    def thread(self, sleep_time: int, thread_name):
        debugger("threader - thread |adding job |'%s' '%s' |interval '%s' '%s'" % (type(thread_name), thread_name, type(sleep_time), sleep_time))

        def decorator(function):
            if sleep_time == 0:
                sleep_time_new = 600
                self.jobs.append(Job(timedelta(seconds=sleep_time_new), function, thread_name, run_once=True))
            else: self.jobs.append(Job(timedelta(seconds=sleep_time), function, thread_name))
            return function
        return decorator

    def block_root_process(self):
        debugger("threader - block |running threads in foreground")
        LogWrite("Starting threads in foreground", level=3)
        while True:
            try:
                time_sleep(1)
            except:
                self.stop()
                raise SystemExit

    def stop(self):
        debugger("threader - stop |stopping jobs")
        for job in self.jobs: job.stop()
        LogWrite("All threads stopped. Exiting loop", level=2)

    def stop_thread(self, thread_name):
        debugger("threader - stop_thread |'%s' '%s'" % (type(thread_name), thread_name))
        to_process_list = self.jobs
        for job in to_process_list:
            if job.name == thread_name:
                job.stop()
                self.jobs.remove(job)
                LogWrite("Thread %s stopped." % job.name, level=2)

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
