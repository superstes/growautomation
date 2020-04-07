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
        LogWrite("Thread of function  '%s' started" % self.execute.__name__, loglevel=4)
        while not self.state_stop.wait(self.interval.total_seconds()):
            self.execute(*self.args, **self.kwargs)
            if self.state_stop.isSet():
                LogWrite("Exiting thread of function '%s'" % self.execute.__name__, loglevel=4)
                break


class Loop:
    def __init__(self):
        self.jobs = []

    def start(self, deamon=True):
        if deamon is False:
            LogWrite("Starting threads in foreground", loglevel=3)
        else:
            LogWrite("Starting threads in background", loglevel=3)
        for j in self.jobs:
            j.daemon = deamon
            j.start()

        if not deamon:
            self.block_root_process()

    def thread(self, sleeptime, thread_name):
        def decorator(function):
            self.add_thread(function, timedelta(seconds=sleeptime), thread_name)
            return function
        return decorator

    def add_thread(self, function, sleep, name, *args, **kwargs):
        self.jobs.append(Job(sleep, function, name, *args, **kwargs))

    def block_root_process(self):
        while True:
            try:
                time_sleep(1)
            except:
                self.stop()
                raise SystemExit

    def stop(self):
        for j in self.jobs:
            j.stop()
        LogWrite("All threads stopped. Exiting loop", loglevel=2)

    def stop_thread(self, name_list):
        to_process_list = self.jobs
        for j in to_process_list:
            if j.name in name_list:
                j.stop()
                self.jobs.remove(j)
                LogWrite("Thread %s stopped." % j.name, loglevel=2)

    def list(self):
        job_name_list = []
        for j in self.jobs:
            job_name_list.append(j.name)
        return job_name_list
