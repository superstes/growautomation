# handles input processing

from core.input.check import Go as Check
from core.input.process import Go as Process
from core.config.object.data.db import GaDataDb
from core.config.db.template import DEVICE_DICT


class Go:
    SQL_DATA_COMMAND = DEVICE_DICT['data']
    SQL_TASK_COMMAND = DEVICE_DICT['task']
    TASK_CATEGORY = 'input'

    def __init__(self, instance):
        self.instance = instance
        self.database = GaDataDb()

    def start(self):
        task_instance_list = Check(instance=self.instance).get()

        for task_instance in task_instance_list:
            data = Process(instance=task_instance).start()

            if data is None:
                self.database.put(command=self.SQL_TASK_COMMAND % ('failure', 'No data received', self.TASK_CATEGORY,
                                                                   task_instance.object_id))
            else:
                self.database.put(command=self.SQL_DATA_COMMAND % (self.instance.object_id, data))
                self.database.put(command=self.SQL_TASK_COMMAND % ('success', 'Data received', self.TASK_CATEGORY,
                                                                   task_instance.object_id))

        self.database.disconnect()
