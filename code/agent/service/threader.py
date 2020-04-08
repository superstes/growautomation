# source: https://github.com/sankalpjonn/timeloop
# modified for use in ga

from threading import Thread, Event
from time import sleep as time_sleep
from datetime import timedelta

from ga.core.ant import LogWrite


class Job(Thread):
    def __init__(self, interval, execute, name, *args, **kwargs):
        Thread.__init__(self)
        self.state_stop = Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs
        self.name = name

    def stop(self):
        self.state_stop.set()
        self.join()
        LogWrite("Thread of function  '%s' stopped" % self.execute.__name__, loglevel=3)

    def run(self):
        LogWrite("Thread of function  '%s' started for '%s'" % (self.execute.__name__, self.name), loglevel=4)
        while not self.state_stop.wait(self.interval.total_seconds()):
            self.execute(*self.args, **self.kwargs)
            if self.state_stop.isSet():
                LogWrite("Exiting thread of function '%s'" % self.execute.__name__, loglevel=4)
                break


class Loop:
    def __init__(self):
        self.jobs = []

    def start(self, daemon=True, single_thread=None):
        if daemon is False:
            LogWrite("Starting threads in foreground", loglevel=3)
        else:
            LogWrite("Starting threads in background", loglevel=3)
            for job in self.jobs:
                if single_thread is not None:
                    if job.name == single_thread:
                        job.daemon = daemon
                        job.start()
                else:
                    job.daemon = daemon
                    job.start()
        if not daemon:
            self.block_root_process()

    def thread(self, sleep_time, thread_name, *args, **kwargs):
        def decorator(function):
            self.jobs.append(Job(timedelta(sleep_time), function, thread_name, *args, **kwargs))
            return function
        return decorator

    def block_root_process(self):
        while True:
            try:
                time_sleep(1)
            except:
                self.stop()
                raise SystemExit

    def stop(self):
        for job in self.jobs:
            job.stop()
        LogWrite("All threads stopped. Exiting loop", loglevel=2)

    def stop_thread(self, thread_name):
        to_process_list = self.jobs
        for job in to_process_list:
            if job.name == thread_name:
                job.stop()
                self.jobs.remove(job)
                LogWrite("Thread %s stopped." % job.name, loglevel=2)

    def reload_thread(self, sleep_time, thread_name, *args, **kwargs):
        self.stop_thread(thread_name)
        self.thread(sleep_time, thread_name, *args, **kwargs)
        self.start(single_thread=thread_name)

    def list(self):
        job_name_list = []
        for job in self.jobs:
            job_name_list.append(job.name)
        return job_name_list
