# handles output processing

from core.device.check import Go as Check
from core.config.object.data.db import GaDataDb
from core.config.db.template import DEVICE_DICT
from core.utils.threader import Loop as Thread
from core.device.output.condition.link import Go as GetGroupResult
from core.device.process import Go as Process
from core.device.log import device_logger

from core.config.object.setting.condition import GaConditionGroup
from core.config.object.device.output import GaOutputDevice
from core.config.object.device.output import GaOutputModel


class Go:
    SQL_TASK_COMMAND = DEVICE_DICT['task']
    TASK_CATEGORY = 'output'
    ALLOWED_OBJECT = GaConditionGroup
    REVERSE_KEY_TIME = 'time'

    def __init__(self, instance):
        self.instance = instance
        self.database = GaDataDb()
        self.output_instance_list = []
        self.processed_list = []
        self.logger = device_logger(addition=instance.name)

    def start(self):
        condition_result = GetGroupResult(group=self.instance).go()

        self._evaluate(condition_result=condition_result)

        self.database.disconnect()

    def _evaluate(self, condition_result):
        if condition_result:
            self.logger.write("Conditions for device \"%s\" were met" % self.instance.name, level=6)

            task_instance_list = Check(
                instance=self.instance,
                model_obj=GaOutputModel,
                device_obj=GaOutputDevice
            ).get()

            for task_instance in task_instance_list:
                # task_id = task_instance.object_id

                result = Process(
                    instance=task_instance,
                    category=self.TASK_CATEGORY
                )

                if result is None:
                    self.logger.write("Processing of %s-device \"%s\" failed" % (self.TASK_CATEGORY, task_instance.name), level=3)
                    # self._task_log(result='failure', msg='No data received', task_id=task_id)

                elif result is False:
                    self.logger.write("Device \"%s\" is in fail-sleep" % task_instance.name, level=4)
                    # self._task_log(result='failure', msg='In fail-sleep', task_id=task_id)

                else:
                    self.logger.write("Processing of output \"%s\" succeeded" % task_instance.name, level=7)
                    # self._task_log(result='success', msg='Executed', task_id=task_id)

                    if task_instance.reverse and task_instance.reverse_type == self.REVERSE_KEY_TIME:
                        self._reverse_timer(instance=task_instance)

        else:
            self.logger.write("Conditions for device \"%s\" were not met" % self.instance.name, level=4)
            # self._task_log(result='failure', msg='Condition not met', task_id=task_id)

    def _reverse_timer(self, instance):
        self.logger.write("Starting reverse timer for %s-device \"%s\" - will be started in \"%s\" secs"
                          % (self.TASK_CATEGORY, instance.name, instance.reverse_timer), level=6)

        thread = Thread()

        @thread.thread(sleep_time=int(instance.reverse_timer), thread_instance=instance, once=True)
        def thread_task(thread_instance, start=False):
            Process(instance=thread_instance, category=self.TASK_CATEGORY, reverse=True).start()

        thread_task(thread_instance=instance)

    # def _task_log(self, result: str, msg: str, task_id: int):
    #     if shared_vars.TASK_LOG:
    #         self.database.put(command=self.SQL_TASK_COMMAND % (result, msg, self.TASK_CATEGORY, task_id))

    def __del__(self):
        self.database.disconnect()
