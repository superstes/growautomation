# handles output processing

from core.device.check import Go as Check
from core.config.object.data.db import GaDataDb
from core.config.db.template import DEVICE_TMPL
from core.utils.threader import Loop as Thread
from core.device.output.condition.link import Go as GetGroupResult
from core.device.process import Go as Process
from core.utils.debug import device_log
from core.config import shared as config

from core.config.object.device.output import GaOutputDevice, GaOutputModel
from core.config.object.setting.condition import GaConditionGroup

from time import sleep
from datetime import datetime


class Go:
    SQL_TASK_COMMAND = DEVICE_TMPL['task']
    SQL_STATE_PUT_COMMAND = DEVICE_TMPL['output']['state']['put']
    SQL_STATE_UPDATE_COMMAND = DEVICE_TMPL['output']['state']['update']
    SQL_STATE_GET_COMMAND = DEVICE_TMPL['output']['state']['get']
    SQL_LOG_COMMAND = DEVICE_TMPL['output']['log']

    def __init__(self, instance: (GaOutputModel, GaOutputDevice, GaConditionGroup), action: str = None, manually: bool = False):
        self.instance = instance
        self.database = GaDataDb()
        self.output_instance_list = []
        self.processed_list = []
        self.action = action
        self.name = instance.name
        self.manually = manually

    def start(self) -> bool:
        if self.manually:  # if the action is triggered manually by the user we don't want to check the conditions
            _ = 'stopp' if self.action == 'stop' else self.action
            device_log(f"{_.capitalize()}ing \"{self.instance.name}\" manually", add=self.name, level=5)
            return self._run()

        elif GetGroupResult(group=self.instance).go():
            device_log(f"Conditions for \"{self.instance.name}\" were met", add=self.name, level=6)
            return self._run()

        else:
            device_log(f"Conditions for \"{self.instance.name}\" were not met", add=self.name, level=3)
            return False

    def _run(self) -> bool:
        if self.manually:
            if type(self.instance) == GaOutputModel:
                output_list = self.instance.member_list

            elif type(self.instance) == GaOutputDevice:
                output_list = [self.instance]

            else:
                device_log(f'Manual execution only allows OutputModels and OutputDevices to be supplied - got neither!', add=self.name, level=3)
                return False

            device_log(f"Output list to process: \"{output_list}\"", add=self.name, level=7)
            areas = None

        else:  # service will always supply a GaConditionGroup
            output_list = self.instance.output_object_list.copy()
            device_log(f"Output list of \"{self.instance.name}\": \"{output_list}\"", add=self.name, level=7)
            output_list.extend(self.instance.output_group_list)
            device_log(f"Output-group list of \"{self.instance.name}\": \"{self.instance.output_group_list}\"", add=self.name, level=7)
            areas = self.instance.area_group_list

        task_instance_list = []

        for output in output_list:
            task_instance_list.extend(
                Check(
                    instance=output,
                    model_obj=GaOutputModel,
                    device_obj=GaOutputDevice,
                    areas=areas,
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
        device_log(f"Processing device instance: \"{device.__dict__}\"", add=self.name, level=7)

        if self.action == 'stop':
            reverse = True
            device_log(f"Device instance: \"{device.__dict__}\" is reversing", add=self.name, level=8)

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

            self._set_or_update_state(device=device)
            if device.active:
                self.database.put(self.SQL_LOG_COMMAND % (datetime.now(), 'start', 'manually' if self.manually else 'auto', device.object_id))

            elif reverse and not device.active:
                # if device was reversed
                self.database.put(self.SQL_LOG_COMMAND % (datetime.now(), 'reverse', 'manually' if self.manually else 'auto', device.object_id))

            device_log(f"Checking device \"{device.name}\" for reversion: reversible - {device.reverse}, active - {device.active}, "
                       f"reverse-type - {device.reverse_type}={config.REVERSE_KEY_TIME}", add=self.name, level=7)

            if not self.manually and device.reverse == 1 and device.active:
                # if device was started
                # if a user executes the action manually he/she/it will know better; they can reverse it manually if needed
                if device.reverse_type == config.REVERSE_KEY_TIME:
                    self._reverse_timer(task_dict=task_dict)

                elif device.reverse_type == config.REVERSE_KEY_CONDITION:
                    self._reverse_condition(task_dict=task_dict)

            return True

    def _set_or_update_state(self, device: GaOutputDevice):
        _db_state = self.database.get(self.SQL_STATE_GET_COMMAND % device.object_id)

        if _db_state is None or len(_db_state) == 0:
            self.database.put(
                self.SQL_STATE_PUT_COMMAND % (
                    datetime.now(),
                    datetime.now(),
                    1 if device.active else 0,
                    datetime.now() if device.reverse_type == config.REVERSE_KEY_TIME else None,
                    device.object_id,
                )
            )

        else:
            self.database.put(
                self.SQL_STATE_UPDATE_COMMAND % (
                    datetime.now(),
                    1 if device.active else 0,
                    datetime.now() if device.reverse_type == config.REVERSE_KEY_TIME else None,
                    device.object_id,
                )
            )

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
            tries = 0

            while not self._process(task_dict=data, reverse=True):
                if config.REVERSE_CONDITION_MAX_RETRIES is not None and tries >= config.REVERSE_CONDITION_MAX_RETRIES:
                    device_log(f"Reversing of device \"{device.name}\" failed: reached maximum number of retries {tries}", add=self.name, level=3)
                    break

                device_log(f"Reversing of device \"{device.name}\" continues", add=self.name, level=8)
                sleep(config.REVERSE_CONDITION_INTERVAL)
                tries += 1

            if config.REVERSE_CONDITION_MAX_RETRIES is None or tries < config.REVERSE_CONDITION_MAX_RETRIES:
                device_log(f"Reversing of device \"{device.name}\" finished", add=self.name, level=6)

            thread.stop_thread(description=device.name)

        thread.start()
