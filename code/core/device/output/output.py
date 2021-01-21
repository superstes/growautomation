# handles output processing

from core.device.check import Go as Check
from core.config.object.data.db import GaDataDb
from core.config.db.template import DEVICE_DICT
from core.config import shared as shared_vars
from core.utils.threader import Loop as Thread
from core.utils.debug import debugger
from core.device.output.condition.link import Go as GetGroupResult
from core.device.process import Go as Process

from core.config.object.setting.condition import GaConditionGroup
from core.config.object.device.output import GaOutputDevice
from core.config.object.device.output import GaOutputModel


class Go:
    SQL_TASK_COMMAND = DEVICE_DICT['task']
    TASK_CATEGORY = 'output'
    ALLOWED_OBJECT = GaConditionGroup

    def __init__(self, instance):
        self.instance = instance
        self.CONFIG = shared_vars.CONFIG
        self.database = GaDataDb()
        self.output_instance_list = []
        self.processed_list = []

    def start(self):
        condition_result = GetGroupResult(group=self.instance).go()

        self._evaluate(condition_result=condition_result)

        self.database.disconnect()

    def _evaluate(self, condition_result):
        if condition_result is True:
            debugger("device-output | _evaluate | conditions were met: \"%s\"" % self.instance.name)

            task_instance_list = Check(
                instance=self.instance,
                model_obj=GaOutputModel,
                device_obj=GaOutputDevice
            ).get()

            for task_instance in task_instance_list:
                Process(
                    instance=task_instance,
                    category=self.TASK_CATEGORY
                )

                debugger("device-output | _evaluate | processing of output \"%s\" succeeded" % task_instance.name)

                if task_instance.reverse and task_instance.reverse_type == GaOutputDevice.REVERSE_TYPE_TIME:
                    self._reverse_timer(instance=task_instance)

                if shared_vars.TASK_LOG:
                    self.database.put(self.SQL_TASK_COMMAND % ('success', 'Executed', self.TASK_CATEGORY,
                                                               task_instance.object_id))
        else:
            debugger("device-output | _evaluate | conditions were not met: \"%s\"" % self.instance.name)

            if shared_vars.TASK_LOG:
                self.database.put(self.SQL_TASK_COMMAND % ('aborted', 'Condition not met', self.TASK_CATEGORY,
                                                           self.instance.object_id))

    def _reverse_timer(self, instance):
        debugger("device-output | _reverse_timer | starting reverse timer for output \"%s\" - \"%s\" secs"
                 % (instance.name, instance.reverse_timer))

        thread = Thread()

        @thread.thread(sleep_time=int(instance.reverse_timer), thread_instance=instance, once=True)
        def thread_task(thread_instance, start=False):
            Process(instance=thread_instance, category=self.TASK_CATEGORY, reverse=True).start()

        thread_task(thread_instance=instance)
