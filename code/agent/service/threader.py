# source: https://github.com/sankalpjonn/timeloop
# modified for use in ga

# ga_version0.3

from ga.core.ant import LogWrite

from threading import Thread, Event
from time import sleep as time_sleep
from datetime import timedelta
from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe

LogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), level=2)


class Job(Thread):
    def __init__(self, interval, execute, name, run_once=False, debug=False):
        Thread.__init__(self)
        self.state_stop = Event()
        self.interval = interval
        self.execute = execute
        self.name = name
        self.run_once = run_once
        self.debug = debug

    def stop(self):
        if self.debug: print("threader - thread stopping", self.name)
        self.state_stop.set()
        self.join()
        LogWrite("Stopped thread '%s'" % self.name, level=3)

    def run(self):
        LogWrite("Starting thread '%s'" % self.name, level=4)
        if self.debug: print("threader - thread starting", self.name)
        if self.run_once:
            self.execute()
            Loop.stop_thread(self.name)
        else:
            while not self.state_stop.wait(self.interval.total_seconds()):
                self.execute()
                if self.state_stop.isSet():
                    if self.debug: print("threader - thread exiting", self.name)
                    LogWrite("Exiting thread '%s'" % self.name, level=4)
                    break


class Loop:
    def __init__(self):
        self.jobs = []
        self.debug = False

    def start(self, daemon=True, single_thread=None):
        LogWrite("Starting threads in background", level=3)
        for job in self.jobs:
            if single_thread is not None:
                if self.debug: print("threader - starting thread", type(single_thread), single_thread)
                if job.name == single_thread:
                    job.daemon = daemon
                    job.start()
            else:
                if self.debug: print("threader - starting threads")
                job.daemon = daemon
                job.start()
        if not daemon: self.block_root_process()

    def thread(self, sleep_time: int, thread_name, debug=False):
        self.debug = debug
        if self.debug: print("threader - adding job", type(thread_name), thread_name, "|interval", type(sleep_time), sleep_time)

        def decorator(function):
            if sleep_time == 0:
                sleep_time_new = 600
                self.jobs.append(Job(timedelta(seconds=sleep_time_new), function, thread_name, run_once=True, debug=self.debug))
            else: self.jobs.append(Job(timedelta(seconds=sleep_time), function, thread_name, debug=self.debug))
            return function
        return decorator

    def block_root_process(self):
        if self.debug: print("threader - running in foreground")
        LogWrite("Starting threads in foreground", level=3)
        while True:
            try:
                time_sleep(1)
            except:
                self.stop()
                raise SystemExit

    def stop(self):
        if self.debug: print("threader - stopping jobs")
        for job in self.jobs: job.stop()
        LogWrite("All threads stopped. Exiting loop", level=2)

    def stop_thread(self, thread_name):
        if self.debug: print("threader - stopping thread", type(thread_name), thread_name)
        to_process_list = self.jobs
        for job in to_process_list:
            if job.name == thread_name:
                job.stop()
                self.jobs.remove(job)
                LogWrite("Thread %s stopped." % job.name, level=2)

    def reload_thread(self, sleep_time: int, thread_name):
        if self.debug: print("threader - reloading thread", type(thread_name), thread_name, "|interval", type(sleep_time), sleep_time)
        self.stop_thread(thread_name)
        self.thread(sleep_time, thread_name)
        self.start(single_thread=thread_name)

    def list(self):
        if self.debug: print("threader - listing threads")
        job_name_list = []
        for job in self.jobs: job_name_list.append(job.name)
        return job_name_list
