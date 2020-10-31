# handles output processing

from core.device.output.check import Go as Check
from core.device.output.process import Go as Process
from core.device.output.condition.condition import Go as Condition
from core.config.object.data.db import GaDataDb
from core.config.db.template import DEVICE_DICT
from core.config import shared as shared_vars


class Go:
    SQL_TASK_COMMAND = DEVICE_DICT['task']
    TASK_CATEGORY = 'output'

    def __init__(self, instance):
        self.instance = instance
        self.database = GaDataDb()

    def start(self):
        task_instance_list = Check(instance=self.instance).get()

        for task_instance in task_instance_list:
            if Condition(instance=task_instance).get():
                if Process(instance=task_instance).start():
                    if shared_vars.TASK_LOG:
                        self.database.put(self.SQL_TASK_COMMAND % ('failure', 'Execution stopped', self.TASK_CATEGORY,
                                                                   task_instance.object_id))
                else:
                    if shared_vars.TASK_LOG:
                        self.database.put(self.SQL_TASK_COMMAND % ('success', 'Executed', self.TASK_CATEGORY,
                                                                   task_instance.object_id))
                    # log error or whatever

        self.database.disconnect()
