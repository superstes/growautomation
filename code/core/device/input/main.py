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

    def __init__(self, instance):
        self.instance = instance
        self.database = GaDataDb()
        self.logger = device_logger(addition=instance.name)

    def start(self):
        task_instance_list = Check(
            instance=self.instance,
            model_obj=GaInputModel,
            device_obj=GaInputDevice,
        ).get()

        for task_dict in task_instance_list:
            device = task_dict['device']
            task_name = device.name
            task_id = device.object_id
            self.logger.write(f"Processing device instance: \"{device.__dict__}\"", level=7)

            if 'downlink' in task_dict:
                data = Process(instance=task_dict['downlink'], nested_instance=device, script_dir='connection').start()

            else:
                data = Process(instance=device, script_dir='input').start()

            if data is None:
                self.logger.write(f"No data received for device \"{task_name}\"", level=3)

            elif data is False:
                self.logger.write(f"Device \"{task_name}\" is in fail-sleep", level=4)

            else:
                self.database.put(command=self.SQL_DATA_COMMAND % (datetime.now(), data, task_id))
                self.logger.write(f"Processing of input-device \"{task_name}\" succeeded", level=7)
