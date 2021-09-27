# runs service timers in multiple threads
# base code source: https://github.com/sankalpjonn/timeloop
# modified for use in GrowAutomation

from core.utils.debug import log

from threading import Thread, Event
from time import sleep as time_sleep
from datetime import timedelta
from sys import exc_info as sys_exc_info
from traceback import format_exc


class Workload(Thread):
    JOIN_TIMEOUT = 5
    MAX_TRACEBACK_LENGTH = 5000
    FAIL_COUNT_SLEEP = 5
    FAIL_SLEEP = 600

    def __init__(self, sleep: timedelta, execute, data, loop_instance, description: str, once: bool = False):
        Thread.__init__(self)
        self.sleep = sleep
        self.execute = execute  # function to execute
        self.data = data
        self.loop_instance = loop_instance
        self.once = once
        self.state_stop = Event()
        self.description = description
        self.log_name = f"\"{self.name}\" (\"{description}\")"
        self.fail_count = 0

    def stop(self) -> bool:
        log(f"Thread stopping \"{self.log_name}\"", level=6)
        self.state_stop.set()

        try:
            self.join(self.JOIN_TIMEOUT)
            if self.is_alive():
                log(f"Unable to join thread \"{self.log_name}\"", level=5)

        except RuntimeError:
            pass

        log(f"Stopped thread \"{self.log_name}\"", level=4)
        return True

    def run(self) -> None:
        if self.fail_count >= self.FAIL_COUNT_SLEEP:
            log(f"Thread \"{self.log_name}\" failed too often => entering fail-sleep of {self.FAIL_SLEEP} secs", level=3)
            time_sleep(self.FAIL_SLEEP)

        log(f"Entering runtime of thread \"{self.log_name}\"", level=7)
        try:
            if self.once:
                while not self.state_stop.wait(self.sleep.total_seconds()):
                    self.execute(data=self.data)
                    Loop.stop_thread(self.loop_instance, description=self.description)
                    break

            else:
                while not self.state_stop.wait(self.sleep.total_seconds()):
                    if self.state_stop.isSet():
                        log(f"Exiting thread \"{self.log_name}\"", level=5)
                        break

                    else:
                        log(f"Starting thread \"{self.log_name}\"", level=5)
                        self.execute(data=self.data)

        except (RuntimeError, ValueError, IndexError, KeyError, AttributeError, TypeError) as error_msg:
            self.fail_count += 1
            log(f"Thread \"{self.log_name}\" failed with error: \"{error_msg}\"", level=1)
            log(f"{format_exc()}"[:self.MAX_TRACEBACK_LENGTH], level=4)

            if not self.once:
                self.run()

        except:
            self.fail_count += 1
            exc_type, exc_obj, _ = sys_exc_info()
            log(f"Thread \"{self.log_name}\" failed with error: \"{exc_type} - {exc_obj}\"", level=1)
            log(f"{format_exc()}"[:self.MAX_TRACEBACK_LENGTH], level=4)

            if not self.once:
                self.run()


class Loop:
    DEFAULT_SLEEP_TIME = 600

    def __init__(self):
        self.jobs = []

    def start(self, daemon=True, single_thread: str = None) -> None:
        if daemon:
            log('Starting threads in background', level=6)

        for job in self.jobs:
            if single_thread is None:
                job.daemon = daemon
                job.start()

            else:
                log(f"Starting single thread \"{single_thread}\"", level=6)

                if job.description == single_thread:
                    job.daemon = daemon
                    job.start()

        if daemon is False:
            log('Starting threads in foreground', level=3)
            self._block_root_process()

    def thread(self, sleep_time: int, thread_data, description: str, once: bool = False):
        log(f"Adding thread for \"{description}\" with interval \"{sleep_time}\"", level=7)

        def decorator(function):
            if sleep_time == 0:
                sleep_time_new = self.DEFAULT_SLEEP_TIME
                self.jobs.append(
                    Workload(
                        sleep=timedelta(seconds=sleep_time_new),
                        execute=function,
                        data=thread_data,
                        loop_instance=self,
                        once=True,
                        description=description,
                    )
                )
            else:
                self.jobs.append(
                    Workload(
                        sleep=timedelta(seconds=sleep_time),
                        execute=function,
                        data=thread_data,
                        loop_instance=self,
                        once=once,
                        description=description,
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
        log('Stopping all thread jobs', level=6)

        for job in self.jobs:
            job.stop()

        log('All threads stopped. Exiting loop', level=3)
        return True

    def stop_thread(self, description: str):
        log(f"Stopping thread for \"{description}\"", level=6)
        to_process_list = self.jobs

        for job in to_process_list:
            if job.description == description:
                job.stop()
                self.jobs.remove(job)
                log(f"Thread {job.description} stopped.", level=4)

    def start_thread(self, sleep_time: int, thread_data, description: str) -> None:
        self.thread(
            sleep_time=sleep_time,
            thread_data=thread_data,
            description=description,
        )
        self.start(single_thread=thread_data)

    def reload_thread(self, sleep_time: int, thread_data, description: str) -> None:
        log(f"Reloading thread for \"{description}\"", level=6)
        self.stop_thread(description=description)
        self.start_thread(
            sleep_time=sleep_time,
            thread_data=thread_data,
            description=description,
        )

    def list(self) -> list:
        log('Returning thread list', level=8)
        return [job.data for job in self.jobs]
