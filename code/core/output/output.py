# handles output processing

from core.output.check import Go as Check
from core.output.process import Go as Process
from core.output.condition.condition import Go as Condition
from core.config.object.data.db import GaDataDb
from core.config.db.template import DEVICE_DICT


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
                    self.database.put(self.SQL_TASK_COMMAND % ('failure', 'Execution stopped', self.TASK_CATEGORY,
                                                               task_instance.object_id))
                else:
                    self.database.put(self.SQL_TASK_COMMAND % ('success', 'Executed', self.TASK_CATEGORY,
                                                               task_instance.object_id))
                    # log error or whatever

        self.database.disconnect()
