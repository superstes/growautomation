# runs service timers in multiple threads
# base code source: https://github.com/sankalpjonn/timeloop
# modified for use in growautomation

from core.utils.debug import Log
from core.utils.debug import debugger

from threading import Thread, Event
from time import sleep as time_sleep
from datetime import timedelta


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

    def stop(self) -> bool:
        debugger("utils-threader | workload-stop | thread stopping \"%s\" (\"%s\")" % (self.name, self.instance.name))
        self.state_stop.set()
        try:
            self.join(self.JOIN_TIMEOUT)
            if self.is_alive():
                debugger("utils-threader | workload-stop | unable to join thread \"%s\" (\"%s\")"
                         % (self.name, self.instance.name))
        except RuntimeError:
            pass
        self.logger.write("Stopped thread \"%s\"" % self.instance.name, level=3)
        return True

    def run(self) -> None:
        try:
            self.logger.write("Starting thread \"%s\"" % self.instance.name, level=4)
            debugger("utils-threader | workload-run | thread runtime \"%s\" (\"%s\")" % (self.name, self.instance.name))
            if self.once:
                self.execute()
                Loop.stop_thread(self.loop_instance, thread_instance=self.instance)
            else:
                while not self.state_stop.wait(self.sleep.total_seconds()):
                    if self.state_stop.isSet():
                        debugger("utils-threader | workload-run | thread exiting \"%s\" (\"%s\")"
                                 % (self.name, self.instance.name))
                        self.logger.write("Exiting thread \"%s\"" % self.instance.name, level=4)
                        break
                    else:
                        debugger("utils-threader | workload-run | thread starting \"%s\" (\"%s\")"
                                 % (self.name, self.instance.name))
                        self.execute(thread_instance=self.instance, start=True)
        except (RuntimeError,
                ValueError,
                IndexError,
                KeyError,
                AttributeError,
                TypeError
                ) as error_msg:
            debugger("utils-threader | workload-run | thread \"%s\" (\"%s\") error occurred: \"%s\""
                     % (self.name, self.instance.name, error_msg))
            self.logger.write("Returning to runtime of thread \"%s\" (\"%s\") because the following error occurred: \"%s\""
                        % (self.name, self.instance.name, error_msg))
            self.run()


class Loop:
    def __init__(self):
        self.jobs = []
        self.logger = Log()

    def start(self, daemon=True, single_thread=None) -> None:
        self.logger.write('Starting threads in background', level=3)
        for job in self.jobs:
            job.daemon = daemon
            if single_thread is not None:
                debugger('utils-threader | loop-start | starting single_thread')
                if job.name == single_thread:
                    job.start()
            else:
                job.start()
        if daemon is False:
            self._block_root_process()

    def thread(self, sleep_time: int, thread_instance, once: bool = False):
        debugger("utils-threader | loop-thread | adding job \"%s\", interval \"%s\" \"%s\""
                 % (thread_instance.name, type(sleep_time), sleep_time))

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
        debugger('utils-threader | loop-block | running threads in foreground')
        self.logger.write('Starting threads in foreground', level=3)
        while True:
            try:
                time_sleep(1)
            except KeyboardInterrupt:
                self.stop()

    def stop(self) -> bool:
        debugger('utils-threader | loop-stop | stopping jobs')
        for job in self.jobs:
            job.stop()
        self.logger.write('All threads stopped. Exiting loop', level=2)
        return True

    def stop_thread(self, thread_instance):
        debugger("utils-threader | loop-stop_thread | \"%s\"" % thread_instance.name)
        to_process_list = self.jobs
        for job in to_process_list:
            if job.name == thread_instance:
                job.stop()
                self.jobs.remove(job)
                self.logger.write("Thread %s stopped." % job.name, level=2)

    def start_thread(self, sleep_time: int, thread_instance) -> None:
        debugger("utils-threader | loop-start_thread | \"%s\", interval \"%s\" \"%s\""
                 % (thread_instance.name, type(sleep_time), sleep_time))
        self.thread(sleep_time, thread_instance)
        self.start(single_thread=thread_instance)

    def reload_thread(self, sleep_time: int, thread_instance) -> None:
        debugger("utils-threader | loop-reload_thread | \"%s\", interval \"%s\" \"%s\""
                 % (thread_instance.name, type(sleep_time), sleep_time))
        self.stop_thread(thread_instance)
        self.start_thread(sleep_time, thread_instance)

    def list(self) -> list:
        debugger('utils-threader | loop-list | returning thread list')
        return [job.instance for job in self.jobs]
