# handles input processing

from core.device.check import Go as Check
from core.device.process import Go as Process
from core.config.object.data.db import GaDataDb
from core.config.db.template import DEVICE_DICT
from core.config import shared as shared_vars
from core.config.object.device.input import GaInputDevice
from core.config.object.device.input import GaInputModel
from core.utils.debug import debugger


class Go:
    SQL_DATA_COMMAND = DEVICE_DICT['input']['data']
    SQL_TASK_COMMAND = DEVICE_DICT['task']
    TASK_CATEGORY = 'input'

    def __init__(self, instance):
        self.instance = instance
        self.database = GaDataDb()

    def start(self):
        task_instance_list = Check(instance=self.instance, model_obj=GaInputModel, device_obj=GaInputDevice).get()

        for task_instance in task_instance_list:
            debugger("device-input | start | processing input '%s'" % task_instance.name)
            data = Process(instance=task_instance, category=self.TASK_CATEGORY).start()

            if data is None:
                debugger("device-input | start | no data received for input '%s'" % task_instance.name)

                if shared_vars.TASK_LOG:
                    self.database.put(command=self.SQL_TASK_COMMAND
                                      % ('failure', 'No data received', self.TASK_CATEGORY,
                                         task_instance.object_id))
            else:
                self.database.put(command=self.SQL_DATA_COMMAND % (task_instance.object_id, data,
                                                                   task_instance.datatype))

                debugger("device-input | start | processing of input '%s' succeeded" % task_instance.name)

                if shared_vars.TASK_LOG:
                    self.database.put(command=self.SQL_TASK_COMMAND % ('success', 'Data received', self.TASK_CATEGORY,
                                                                       task_instance.object_id))

        self.database.disconnect()
