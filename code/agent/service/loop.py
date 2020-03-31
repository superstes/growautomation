# source: https://github.com/sankalpjonn/timeloop
# modified for use in ga


from threading import Thread, Event
from signal import signal
from signal import SIGINT
from signal import SIGTERM
from time import sleep as time_sleep
from datetime import timedelta

from ga.core.ant import LogWrite


class Job(Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        Thread.__init__(self)
        self.stopped = Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def stop(self):
        self.stopped.set()
        self.join()

    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            self.execute(*self.args, **self.kwargs)


class Loop:
    def __init__(self, seconds):
        self.jobs = []
        self.seconds = seconds

    def __repr__(self):
        interval = timedelta(seconds=self.seconds)

        def decorator(f):
            self.add_job(f, interval)
            return f
        return decorator

    def add_job(self, func, interval, *args, **kwargs):
        self.jobs.append(Job(interval, func, *args, **kwargs))

    def block(self):
        signal(SIGTERM, self.exit("term"))
        signal(SIGINT, self.exit("int"))

        while True:
            try:
                time_sleep(1)
            except Exception:
                self.stop()
                break

    def start(self, block=False):
        LogWrite("Starting Timeloop")
        for j in self.jobs:
            j.daemon = not block
            j.start()
            LogWrite("Registered job {}".format(j.execute))

        LogWrite("Timeloop now started. Jobs will run based on the interval set")
        if block:
            self.block()

    def stop(self):
        LogWrite("Timeloop exited")
        for j in self.jobs:
            LogWrite("Stopping job {}".format(j.execute))
            j.stop()

    def exit(self, reason):
        LogWrite("Shutting down because of sig%s interrupt" % reason)
        raise SystemExit
