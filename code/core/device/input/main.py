# handles input processing

from core.device.check import Go as Check
from core.device.process import Go as Process
from core.config.object.data.db import GaDataDb
from core.config.db.template import DEVICE_TMPL
from core.utils.debug import device_log

from core.config.object.device.input import GaInputDevice
from core.config.object.device.input import GaInputModel

from datetime import datetime


class Go:
    SQL_DATA_COMMAND = DEVICE_TMPL['input']['data']
    SQL_TASK_COMMAND = DEVICE_TMPL['task']

    def __init__(self, instance: (GaInputDevice, GaInputModel), manually: bool = False):
        self.instance = instance
        self.database = GaDataDb()
        self.name = instance.name
        self.manually = manually

    def start(self) -> bool:
        task_instance_list = Check(
            instance=self.instance,
            model_obj=GaInputModel,
            device_obj=GaInputDevice,
        ).get()

        results = []

        for task_dict in task_instance_list:
            device = task_dict['device']
            task_name = device.name
            task_id = device.object_id
            device_log(f"Processing device instance: \"{device.__dict__}\"", add=self.name, level=7)

            if 'downlink' in task_dict:
                data = Process(
                    instance=task_dict['downlink'],
                    nested_instance=device,
                    script_dir='connection',
                    manually=self.manually,
                ).start()

            else:
                data = Process(
                    instance=device,
                    script_dir='input',
                    manually=self.manually,
                ).start()

            if data is None:
                device_log(f"No data received for device \"{task_name}\"", add=self.name, level=3)
                results.append(False)

            elif data is False:
                device_log(f"Device \"{task_name}\" is in fail-sleep", add=self.name, level=4)
                results.append(False)

            else:
                self.database.put(command=self.SQL_DATA_COMMAND % (datetime.now(), data, task_id))
                device_log(f"Processing of input-device \"{task_name}\" succeeded", add=self.name, level=7)
                results.append(True)

        if len(results) > 0:
            return all(results)

        return False
