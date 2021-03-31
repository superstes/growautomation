# runs service timers in multiple threads
# base code source: https://github.com/sankalpjonn/timeloop
# modified for use in GrowAutomation

from core.utils.debug import Log

from threading import Thread, Event
from time import sleep as time_sleep
from datetime import timedelta
from sys import exc_info as sys_exc_info
from traceback import format_exc


class Workload(Thread):
    JOIN_TIMEOUT = 5

    def __init__(self, sleep, execute, instance, loop_instance, once=False):
        Thread.__init__(self)
        self.sleep = sleep
        self.execute = execute
        self.instance = instance
        self.loop_instance = loop_instance
        self.once = once
        self.state_stop = Event()
        self.logger = Log()
        self.log_name = "\"%s\" (\"%s\")" % (self.name, self.instance.name)

    def stop(self) -> bool:
        self.logger.write("Thread stopping %s" % self.log_name, level=6)
        self.state_stop.set()
        try:
            self.join(self.JOIN_TIMEOUT)
            if self.is_alive():
                self.logger.write("Unable to join thread %s" % self.log_name, level=5)
        except RuntimeError:
            pass
        self.logger.write("Stopped thread %s" % self.log_name, level=4)
        return True

    def run(self) -> None:
        try:
            self.logger.write("Entering runtime of thread %s" % self.log_name, level=7)
            if self.once:
                self.execute()
                Loop.stop_thread(self.loop_instance, thread_instance=self.instance)
            else:
                while not self.state_stop.wait(self.sleep.total_seconds()):
                    if self.state_stop.isSet():
                        self.logger.write("Exiting thread %s" % self.log_name, level=5)
                        break
                    else:
                        self.logger.write("Starting thread %s" % self.log_name, level=5)
                        self.execute(thread_instance=self.instance, start=True)
        except (RuntimeError, ValueError, IndexError, KeyError, AttributeError, TypeError) as error_msg:
            self.logger.write("Thread %s failed with error: \"%s\"\n%s" % (self.log_name, error_msg, format_exc()))
            self.run()

        except:
            exc_type, exc_obj, _ = sys_exc_info()
            self.logger.write("Thread %s failed with error: \"%s - %s\"\n%s" % (self.log_name, exc_type, exc_obj, format_exc()))
            self.run()


class Loop:
    def __init__(self):
        self.jobs = []
        self.logger = Log()

    def start(self, daemon=True, single_thread=None) -> None:
        if daemon:
            self.logger.write('Starting threads in background', level=6)

        for job in self.jobs:
            if single_thread is None:
                job.daemon = daemon
                job.start()

            else:
                self.logger.write("Starting single_thread \"%s\"" % single_thread.name, level=6)

                if job.name == single_thread:
                    job.daemon = daemon
                    job.start()

        if daemon is False:
            self.logger.write('Starting threads in foreground', level=3)
            self._block_root_process()

    def thread(self, sleep_time: int, thread_instance, once: bool = False):
        self.logger.write("Adding thread job \"%s\", interval \"%s\" \"%s\"" % (thread_instance.name, type(sleep_time), sleep_time), level=7)

        def decorator(function):
            if sleep_time == 0:
                sleep_time_new = 600
                self.jobs.append(
                    Workload(
                        sleep=timedelta(seconds=sleep_time_new),
                        execute=function,
                        instance=thread_instance,
                        loop_instance=self,
                        once=True
                    )
                )
            else:
                self.jobs.append(
                    Workload(
                        sleep=timedelta(seconds=sleep_time),
                        execute=function,
                        instance=thread_instance,
                        loop_instance=self,
                        once=once
                    )
                )
            return function
        return decorator

    def _block_root_process(self) -> None:
        while True:
            try:
                time_sleep(1)
            except KeyboardInterrupt:
                self.stop()

    def stop(self) -> bool:
        self.logger.write('Stopping all thread jobs', level=6)

        for job in self.jobs:
            job.stop()

        self.logger.write('All threads stopped. Exiting loop', level=3)
        return True

    def stop_thread(self, thread_instance):
        self.logger.write("Stopping thread \"%s\"" % thread_instance.name, level=6)
        to_process_list = self.jobs

        for job in to_process_list:
            if job.name == thread_instance:
                job.stop()
                self.jobs.remove(job)
                self.logger.write("Thread %s stopped." % job.name, level=2)

    def start_thread(self, sleep_time: int, thread_instance) -> None:
        self.thread(sleep_time, thread_instance)
        self.start(single_thread=thread_instance)

    def reload_thread(self, sleep_time: int, thread_instance) -> None:
        self.logger.write("Reloading thread \"%s\"" % thread_instance.name, level=6)
        self.stop_thread(thread_instance)
        self.start_thread(sleep_time, thread_instance)

    def list(self) -> list:
        self.logger.write('Returning thread list', level=8)
        return [job.instance for job in self.jobs]
