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

    def _evaluate(self, condition_result) -> None:
        # todo: reverse type condition implementation => Ticket#11

        if condition_result:
            self.logger.write(f"Conditions for \"{self.instance.name}\" were met", level=6)

            output_list = self.instance.output_object_list.copy()

            self.logger.write(f"Output list of \"{self.instance.name}\": \"{output_list}\"", level=7)
            output_list.extend(self.instance.output_group_list)
            self.logger.write(f"Output-group list of \"{self.instance.name}\": \"{self.instance.output_group_list}\"", level=7)

            task_instance_list = []

            for output in output_list:
                task_instance_list.extend(
                    Check(
                        instance=output,
                        model_obj=GaOutputModel,
                        device_obj=GaOutputDevice,
                        areas=self.instance.area_group_list,
                    ).get()
                )

            for task_dict in task_instance_list:
                self._process(task_dict=task_dict)

        else:
            self.logger.write(f"Conditions for \"{self.instance.name}\" were not met", level=3)

    def _process(self, task_dict: dict, reverse=False) -> None:
        device = task_dict['device']
        self.logger.write(f"Processing device instance: \"{device.__dict__}\"", level=7)

        if 'downlink' in task_dict:
            result = Process(instance=task_dict['downlink'], nested_instance=device, script_dir='connection', reverse=reverse).start()

        else:
            result = Process(instance=device, script_dir='output', reverse=reverse).start()

        if result is None:
            self.logger.write(f"Processing of output-device \"{device.name}\" failed", level=3)

        elif result is False:
            self.logger.write(f"Device \"{device.name}\" is in fail-sleep", level=4)

        else:
            self.logger.write(f"Processing of output \"{device.name}\" succeeded", level=7)

            self.logger.write(f"Checking device \"{device.name}\" for reversion: reverseable - {device.reverse}, active - {device.active}, "
                              f"reverse-type - {device.reverse_type}={self.REVERSE_KEY_TIME}", level=7)

            if device.reverse == 1 and device.active and device.reverse_type == self.REVERSE_KEY_TIME:
                self._reverse_timer(task_dict=task_dict)

    def _condition_members(self) -> dict:
        output_dict = {}

        if self.instance.output_object_list is not None:
            for device in self.instance.output_object_list:
                output_dict[device] = GaOutputDevice

        if self.instance.output_group_list is not None:
            for device in self.instance.output_group_list:
                output_dict[device] = GaOutputDevice

        return output_dict

    def _reverse_timer(self, task_dict: dict) -> None:
        device = task_dict['device']
        self.logger.write(f"Entering wait timer ({device.reverse_type_data} secs) for output-device \"{device.name}\"", level=6)

        thread = Thread()

        @thread.thread(
            sleep_time=int(device.reverse_type_data),
            thread_data=task_dict,
            once=True,
            description=device.name,
        )
        def thread_task(data):
            self._process(task_dict=data, reverse=True)

        thread.start()

    def __del__(self):
        self.database.disconnect()
