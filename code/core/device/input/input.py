# handles input processing

from core.device.check import Go as Check
from core.device.process import Go as Process
from core.config.object.data.db import GaDataDb
from core.config.db.template import DEVICE_DICT
from core.device.log import device_logger

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
        self.logger = device_logger(addition=instance.name)

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
                data = Process(instance=task_instance['downlink'], category='connection', nested_instance=task_instance['device']).start()

            else:
                task_name = task_instance.name
                task_id = task_instance.object_id

                self.logger.write("Processing device instance: \"%s\"" % task_instance.__dict__, level=6)
                data = Process(instance=task_instance, category=self.TASK_CATEGORY).start()

            if data is None:
                self.logger.write("No data received for device \"%s\"" % task_name, level=3)
                # self._task_log(result='failure', msg='No data received', task_id=task_id)

            elif data is False:
                self.logger.write("Device \"%s\" is in fail-sleep" % task_name, level=4)
                # self._task_log(result='failure', msg='In fail-sleep', task_id=task_id)

            else:
                self.database.put(command=self.SQL_DATA_COMMAND % (datetime.now(), data, task_id))
                self.logger.write("Processing of %s-device \"%s\" succeeded" % (self.TASK_CATEGORY, task_name), level=7)
                # self._task_log(result='success', msg='Data received', task_id=task_id)

    # def _task_log(self, result: str, msg: str, task_id: int):
    #     if shared_vars.TASK_LOG:
    #         self.database.put(command=self.SQL_TASK_COMMAND % (result, msg, self.TASK_CATEGORY, task_id))

    def __del__(self):
        self.database.disconnect()
