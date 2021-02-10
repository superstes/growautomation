# handles input processing

from core.device.check import Go as Check
from core.device.process import Go as Process
from core.config.object.data.db import GaDataDb
from core.config.db.template import DEVICE_DICT
from core.config import shared as shared_vars
from core.utils.debug import MultiLog, Log, debugger

from core.config.object.device.input import GaInputDevice
from core.config.object.device.input import GaInputModel

from datetime import datetime


class Go:
    SQL_DATA_COMMAND = DEVICE_DICT['input']['data']
    SQL_TASK_COMMAND = DEVICE_DICT['task']
    TASK_CATEGORY = 'input'

    def __init__(self, instance):
        self.instance = instance
        self.database = GaDataDb()

        if shared_vars.SYSTEM.device_log == 1:
            self.logger = MultiLog([Log(), Log(typ='device', addition=self.instance.name)])
        else:
            self.logger = Log()

    def start(self):
        task_instance_list = Check(
            instance=self.instance,
            model_obj=GaInputModel,
            device_obj=GaInputDevice
        ).get()

        for task_instance in task_instance_list:
            if type(task_instance) == dict:
                task_name = task_instance['device'].name
                task_id = task_instance['device'].object_id

                self.logger.write("Processing device instance: \"%s\"" % task_instance['device'].__dict__, level=6)
                debugger("device-input | start | processing connection \"%s\"" % task_name)

                data = Process(instance=task_instance['downlink'], category='connection', nested_instance=task_instance['device']).start()

            else:
                task_name = task_instance.name
                task_id = task_instance.object_id

                self.logger.write("Processing device instance: \"%s\"" % task_instance.__dict__, level=6)
                debugger("device-input | start | processing input \"%s\"" % task_name)

                data = Process(instance=task_instance, category=self.TASK_CATEGORY).start()

            if data is None:
                debugger("device-input | start | no data received for input \"%s\"" % task_name)
                self.logger.write("No data received for device \"%s\"" % task_name)

                if shared_vars.TASK_LOG:
                    self.database.put(command=self.SQL_TASK_COMMAND % ('failure', 'No data received', self.TASK_CATEGORY, task_id))
            else:
                self.database.put(command=self.SQL_DATA_COMMAND % (datetime.now(), data, task_id))

                debugger("device-input | start | processing of input \"%s\" succeeded" % task_name)

                if shared_vars.TASK_LOG:
                    self.database.put(command=self.SQL_TASK_COMMAND % ('success', 'Data received', self.TASK_CATEGORY, task_id))

        self.database.disconnect()
