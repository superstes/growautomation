# runs service timers in multiple threads
# base code source: https://github.com/sankalpjonn/timeloop
# modified for use in GrowAutomation

from core.utils.debug import log
from core.config import shared as config

from threading import Thread, Event
from time import sleep as time_sleep
from datetime import timedelta
from sys import exc_info as sys_exc_info
from traceback import format_exc


class Workload(Thread):
    def __init__(self, sleep: timedelta, execute, data, loop_instance, name: str, description: str, once: bool = False, daemon: bool = True):
        Thread.__init__(self, daemon=daemon, name=name)
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
        log(f"Thread stopping {self.log_name}", level=6)
        self.state_stop.set()

        try:
            self.join(config.THREAD_JOIN_TIMEOUT)
            if self.is_alive():
                log(f"Unable to join thread {self.log_name}", level=5)

        except RuntimeError:
            log(f"Got error stopping thread {self.log_name}", level=5)

        log(f"Stopped thread {self.log_name}", level=4)
        return True

    def run(self) -> None:
        if self.fail_count >= config.AGENT.device_fail_count:
            log(f"Thread {self.log_name} failed too often => entering fail-sleep of {config.AGENT.device_fail_sleep} secs", level=3)
            time_sleep(config.AGENT.device_fail_sleep)

        log(f"Entering runtime of thread {self.log_name}", level=7)
        try:
            if self.once:
                while not self.state_stop.wait(self.sleep.total_seconds()):
                    self.execute(data=self.data)
                    Loop.stop_thread(self.loop_instance, description=self.description)
                    break

            else:
                while not self.state_stop.wait(self.sleep.total_seconds()):
                    if self.state_stop.isSet():
                        log(f"Exiting thread {self.log_name}", level=5)
                        break

                    else:
                        log(f"Starting thread {self.log_name}", level=5)
                        self.execute(data=self.data)

        except (RuntimeError, ValueError, IndexError, KeyError, AttributeError, TypeError) as error_msg:
            self.fail_count += 1
            log(f"Thread {self.log_name} failed with error: \"{error_msg}\"", level=1)
            log(f"{format_exc(limit=config.LOG_MAX_TRACEBACK_LENGTH)}", level=4)

            if not self.once:
                self.run()

        except:
            self.fail_count += 1
            exc_type, exc_obj, _ = sys_exc_info()
            log(f"Thread {self.log_name} failed with error: \"{exc_type} - {exc_obj}\"", level=1)
            log(f"{format_exc(limit=config.LOG_MAX_TRACEBACK_LENGTH)}", level=4)

            if not self.once:
                self.run()


class Loop:
    def __init__(self):
        self.jobs = set()
        self.thread_nr = 0

    def start(self) -> None:
        log('Starting all threads', level=6)

        for job in self.jobs:
            job.start()

    def add_thread(self, sleep_time: int, thread_data, description: str, once: bool = False):
        log(f"Adding thread for \"{description}\" with interval \"{sleep_time}\"", level=7)
        self.thread_nr += 1

        def decorator(function):
            if sleep_time == 0:
                sleep_time_new = config.THREAD_DEFAULT_SLEEP_TIME
                self.jobs.add(
                    Workload(
                        sleep=timedelta(seconds=sleep_time_new),
                        execute=function,
                        data=thread_data,
                        loop_instance=self,
                        once=True,
                        description=description,
                        name=f"Thread #{self.thread_nr}",
                    )
                )
            else:
                self.jobs.add(
                    Workload(
                        sleep=timedelta(seconds=sleep_time),
                        execute=function,
                        data=thread_data,
                        loop_instance=self,
                        once=once,
                        description=description,
                        name=f"Thread #{self.thread_nr}",
                    )
                )
            return function
        return decorator

    def stop(self) -> bool:
        log('Stopping all threads', level=6)

        job_list = list(self.jobs)
        job_count = len(job_list)
        for i in range(job_count):
            _ = job_list[i]
            self.jobs.remove(_)
            del _

        log('All threads stopped. Exiting loop', level=3)
        return True

    def stop_thread(self, description: str):
        log(f"Stopping thread for \"{description}\"", level=6)
        for job in self.jobs:
            if job.description == description:
                job.stop()
                self.jobs.remove(job)
                log(f"Thread {job.description} stopped.", level=4)
                del job
                break

    def start_thread(self, description: str) -> None:
        for job in self.jobs:
            if job.description == description:
                job.start()
                log(f"Thread {job.description} started.", level=5)
                break

    def reload_thread(self, sleep_time: int, thread_data, description: str) -> None:
        log(f"Reloading thread for \"{description}\"", level=6)
        self.stop_thread(description=description)
        self.add_thread(
            sleep_time=sleep_time,
            thread_data=thread_data,
            description=description,
        )
        self.start_thread(description=description)

    def list(self) -> list:
        log('Returning thread list', level=8)
        return [job.data for job in self.jobs]

    def __del__(self):
        self.stop()
