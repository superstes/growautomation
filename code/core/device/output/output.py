# handles output processing

from core.device.check import Go as Check
from core.device.process import Go as Process
from core.device.output.condition.condition import Go as Condition
from core.config.object.data.db import GaDataDb
from core.config.db.template import DEVICE_DICT
from core.config import shared as shared_vars
from core.utils.threader import Loop as Thread
from core.utils.debug import debugger

from core.config.object.device.output import GaOutputDevice
from core.config.object.device.output import GaOutputModel


class Go:
    SQL_TASK_COMMAND = DEVICE_DICT['task']
    TASK_CATEGORY = 'output'
    ALLOWED_OBJECT_TUPLE = (GaOutputDevice, GaOutputModel)
    REVERSE_TYPE_TIME = 1
    REVERSE_TYPE_CONDITION = 2

    def __init__(self):
        self.CONFIG = shared_vars.CONFIG
        self.database = GaDataDb()
        self.output_instance_list = []
        self.processed_list = []

    def start(self):
        self._get_output_instances()

        for instance in self.output_instance_list:
            self._output(instance=instance)

        self.database.disconnect()

    def _get_output_instances(self):
        for category, obj_list in self.CONFIG.items():
            for obj in obj_list:
                if isinstance(obj, self.ALLOWED_OBJECT_TUPLE) and obj.enabled:
                    self.output_instance_list.append(obj)

    def _output(self, instance):
        if instance in self.processed_list:
            return None

        task_instance_list = Check(instance=instance, model_obj=GaOutputModel, device_obj=GaOutputDevice).get()

        for task_instance in task_instance_list:
            debugger("device-output | start | processing output '%s'" % task_instance.name)
            if task_instance.active and task_instance.reverse and \
                    task_instance.reverse_type == self.REVERSE_TYPE_CONDITION:
                reverse_condition = True
                debugger("device-output | start | output '%s' needs a reverse condition" % task_instance.name)
            else:
                reverse_condition = False

            if Condition(instance=task_instance, reverse=reverse_condition).get():
                debugger("device-output | start | output '%s' got its conditions met" % task_instance.name)

                if Process(instance=task_instance, category=self.TASK_CATEGORY).start():
                    debugger("device-output | start | processing of output '%s' succeeded" % task_instance.name)

                    if shared_vars.TASK_LOG:
                        self.database.put(self.SQL_TASK_COMMAND % ('failure', 'Execution stopped', self.TASK_CATEGORY,
                                                                   task_instance.object_id))

                    if task_instance.reverse and task_instance.reverse_type == self.REVERSE_TYPE_TIME and \
                            task_instance.active:
                        self._reverse_timer(instance=task_instance)
                else:
                    debugger("device-output | start | processing of output '%s' failed" % task_instance.name)

                    if shared_vars.TASK_LOG:
                        self.database.put(self.SQL_TASK_COMMAND % ('success', 'Executed', self.TASK_CATEGORY,
                                                                   task_instance.object_id))
                    # log error or whatever
            else:
                debugger("device-output | start | conditions for output '%s' not met" % task_instance.name)

        self.processed_list.extend(task_instance_list)

    def _reverse_timer(self, instance):
        debugger("device-output | _reverse_timer | starting reverse timer for output '%s' - '%s' secs"
                 % (instance.name, instance.reverse_timer))

        thread = Thread()

        @thread.thread(sleep_time=int(instance.reverse_timer), thread_instance=instance, once=True)
        def thread_task(thread_instance, start=False):
            Process(instance=thread_instance, category=self.TASK_CATEGORY, reverse=True).start()

        thread_task(thread_instance=instance)
