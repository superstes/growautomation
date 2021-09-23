# handles output processing

from core.device.check import Go as Check
from core.config.object.data.db import GaDataDb
from core.config.db.template import DEVICE_DICT
from core.utils.threader import Loop as Thread
from core.device.output.condition.link import Go as GetGroupResult
from core.device.process import Go as Process
from core.utils.debug import device_log

from core.config.object.device.output import GaOutputDevice, GaOutputModel

from time import sleep


class Go:
    SQL_TASK_COMMAND = DEVICE_DICT['task']
    REVERSE_KEY_TIME = 'time'
    REVERSE_KEY_CONDITION = 'condition'
    REVERSE_CONDITION_INTERVAL = 60

    def __init__(self, instance: (GaOutputModel, GaOutputDevice), action: str = None, manually: bool = True):
        self.instance = instance
        self.database = GaDataDb()
        self.output_instance_list = []
        self.processed_list = []
        self.action = action
        self.name = instance.name
        self.manually = manually

    def start(self) -> bool:
        if self.manually:
            condition_result = True

        else:
            condition_result = GetGroupResult(group=self.instance).go()

        if condition_result:
            device_log(f"Conditions for \"{self.instance.name}\" were met", add=self.name, level=6)

            if self.manually:
                _ = 'stopp' if self.action == 'stop' else self.action
                device_log(f"{_.capitalize()}ing \"{self.instance.name}\" manually", add=self.name, level=5)

            return self._run()

        else:
            device_log(f"Conditions for \"{self.instance.name}\" were not met", add=self.name, level=3)
            return False

    def _run(self) -> bool:
        # todo: reverse type condition implementation => Ticket#11
        output_list = self.instance.output_object_list.copy()
        device_log(f"Output list of \"{self.instance.name}\": \"{output_list}\"", add=self.name, level=7)
        output_list.extend(self.instance.output_group_list)
        device_log(f"Output-group list of \"{self.instance.name}\": \"{self.instance.output_group_list}\"", add=self.name, level=7)

        task_instance_list = []

        for output in output_list:
            task_instance_list.extend(
                Check(
                    instance=output,
                    model_obj=GaOutputModel,
                    device_obj=GaOutputDevice,
                    areas=self.instance.area_group_list,
                    manually=self.manually,
                ).get()
            )

        results = []

        for task_dict in task_instance_list:
            results.append(self._process(task_dict=task_dict))

        if len(results) > 0:
            return all(results)

        return False

    def _process(self, task_dict: dict, reverse=False) -> bool:
        device = task_dict['device']

        if self.action == 'stop':
            reverse = True

        device_log(f"Processing device instance: \"{device.__dict__}\"", add=self.name, level=7)

        if 'downlink' in task_dict:
            result = Process(
                instance=task_dict['downlink'],
                nested_instance=device,
                script_dir='connection',
                reverse=reverse,
                manually=self.manually,
            ).start()

        else:
            result = Process(
                instance=device,
                script_dir='output',
                reverse=reverse,
                manually=self.manually,
            ).start()

        if result is None:
            device_log(f"Processing of output-device \"{device.name}\" failed", add=self.name, level=3)
            return False

        elif result is False:
            device_log(f"Device \"{device.name}\" is in fail-sleep", add=self.name, level=4)
            return False

        else:
            device_log(f"Processing of output \"{device.name}\" succeeded", add=self.name, level=7)

            if not self.manually and device.reverse == 1:  # if a user executes the action manually he/she/it will know better; they can reverse it manually if needed
                device_log(f"Checking device \"{device.name}\" for reversion: reversible - {device.reverse}, active - {device.active}, "
                           f"reverse-type - {device.reverse_type}={self.REVERSE_KEY_TIME}", add=self.name, level=7)

                if device.active:
                    # todo: write state to database => a service restart MUST NOT keep devices running

                    if device.reverse_type == self.REVERSE_KEY_TIME:
                        self._reverse_timer(task_dict=task_dict)

                    elif device.reverse_type == self.REVERSE_KEY_CONDITION:
                        self._reverse_condition(task_dict=task_dict)

                elif reverse and not device.active:
                    # todo: write state (inactive) to database => a service restart MUST NOT keep devices running
                    pass

            return True

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
        device_log(f"Entering wait timer ({device.reverse_type_data} secs) for output-device \"{device.name}\"", add=self.name, level=6)

        thread = Thread()

        @thread.thread(
            sleep_time=int(device.reverse_type_data),
            thread_data=task_dict,
            once=True,
            description=f"Timed reversing for '{device.name}'",
        )
        def thread_task(data):
            self._process(task_dict=data, reverse=True)
            device_log(f"Reversing of device \"{device.name}\" finished", add=self.name, level=6)
            thread.stop_thread(description=device.name)

        thread.start()

    def _reverse_condition(self, task_dict: dict) -> None:
        device = task_dict['device']
        device_log(f"Entering reverse-condition loop for output-device \"{device.name}\"", add=self.name, level=6)

        thread = Thread()

        @thread.thread(
            sleep_time=int(1),
            thread_data=task_dict,
            once=True,
            description=f"Conditional reversing for '{device.name}'",
        )
        def thread_task(data):
            while not self._process(task_dict=data, reverse=True):
                device_log(f"Reversing of device \"{device.name}\" continues", add=self.name, level=8)
                sleep(self.REVERSE_CONDITION_INTERVAL)

            device_log(f"Reversing of device \"{device.name}\" finished", add=self.name, level=6)
            thread.stop_thread(description=device.name)

        thread.start()
