# source: https://github.com/sankalpjonn/timeloop
# modified for use in ga

from threading import Thread, Event
from time import sleep as time_sleep
from datetime import timedelta

from ga.core.ant import LogWrite


class Job(Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        Thread.__init__(self)
        self.state_stop = Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

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
            self.block()

    def job(self, sleeptime):
        def decorator(function):
            self.add_job(function, timedelta(seconds=sleeptime))
            return function
        return decorator

    def add_job(self, function, sleep, *args, **kwargs):
        self.jobs.append(Job(sleep, function, *args, **kwargs))

    def block(self):
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
