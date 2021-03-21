# handles output processing

from core.device.check import Go as Check
from core.config.object.data.db import GaDataDb
from core.config.db.template import DEVICE_DICT
from core.utils.threader import Loop as Thread
from core.device.output.condition.link import Go as GetGroupResult
from core.device.process import Go as Process
from core.device.log import device_logger

from core.config.object.device.output import GaOutputDevice, GaOutputModel


class Go:
    SQL_TASK_COMMAND = DEVICE_DICT['task']
    REVERSE_KEY_TIME = 'time'
    REVERSE_KEY_CONDITION = 'condition'

    def __init__(self, instance):
        self.instance = instance
        self.database = GaDataDb()
        self.output_instance_list = []
        self.processed_list = []
        self.logger = device_logger(addition=instance.name)

    def start(self):
        condition_result = GetGroupResult(group=self.instance).go()

        self._evaluate(condition_result=condition_result)

    def _evaluate(self, condition_result):
        # todo: reverse type condition implementation

        if condition_result:
            self.logger.write(f"Conditions for \"{self.instance.name}\" were met", level=6)

            task_instance_list = Check(
                instance=self.instance,
                model_obj=GaOutputModel,
                device_obj=GaOutputDevice,
                areas=self.instance.area_group_list,
            ).get()

            for task_instance in task_instance_list:
                self._process(task_instance=task_instance)

        else:
            self.logger.write(f"Conditions for \"{self.instance.name}\" were not met", level=4)

    def _process(self, task_instance):
        device = task_instance['device']
        self.logger.write(f"Processing device instance: \"{device.__dict__}\"", level=7)

        if 'downlink' in task_instance:
            result = Process(instance=task_instance['downlink'], nested_instance=device, script_dir='connection').start()

        else:
            result = Process(instance=device, script_dir='output').start()

        if result is None:
            self.logger.write(f"Processing of output-device \"{device.name}\" failed", level=3)

        elif result is False:
            self.logger.write(f"Device \"{device.name}\" is in fail-sleep", level=4)

        else:
            self.logger.write(f"Processing of output \"{device.name}\" succeeded", level=7)

            if device.reverse == 1 and device.active and device.reverse_type == self.REVERSE_KEY_TIME:
                self._reverse_timer(instance=task_instance)

    def _condition_members(self) -> dict:
        output_dict = {}

        if self.instance.output_object_list is not None:
            for device in self.instance.output_object_list:
                output_dict[device] = GaOutputDevice

        if self.instance.output_group_list is not None:
            for device in self.instance.output_group_list:
                output_dict[device] = GaOutputDevice

        return output_dict

    def _reverse_timer(self, instance):
        device = instance['device']
        self.logger.write(f"Starting reverse timer for output-device \"{device.name}\" - will be started "
                          f"in \"{device.reverse_timer}\" secs", level=6)

        thread = Thread()

        @thread.thread(sleep_time=int(device.reverse_timer), thread_instance=device, once=True)
        def thread_task(thread_instance, start=False):
            self._process(task_instance=thread_instance)

        thread_task(thread_instance=instance)

    def __del__(self):
        self.database.disconnect()
