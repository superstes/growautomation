# is called if the service is reloaded
# will find out if some object config has changed
# if so - the service will reload all threads with the new config

# stateful reload todo's:
#   need to have a list of instances(old) of which the config has changed
#   stop all timers etc. off those instances
#     linked instances (group) must also be processed
#   re-create those instances via the factory
#   start the timers for those new instances
#   profit

from core.factory.main import get as factory
from core.factory.forge.blueprint import blueprint_dict
from core.utils.debug import fns_log
from core.config.object.setting.condition import GaConditionGroup, GaConditionLink, GaConditionMatchSpecial, GaConditionMatch
from core.config.object.device.input import GaInputDevice, GaInputModel
from core.config.object.device.output import GaOutputDevice, GaOutputModel
from core.service.timer import get as get_timer

from json import dumps as json_dumps


class Go:
    def __init__(self, object_list: list, config_dict: dict, timers: list):
        self.old_object_list = object_list
        self.old_config_dict = config_dict
        self.new_object_list, self.new_config_dict = factory()
        self.any_changes = self._any_change()
        self.old_timers = timers
        self.reload_categories = {
            'condition': [
                self._get_obj_key(GaConditionLink),
                self._get_obj_key(GaConditionMatchSpecial),
                self._get_obj_key(GaConditionMatch),
                self._get_obj_key(GaConditionGroup),
            ],
            'output': [
                self._get_obj_key(GaOutputDevice),
                self._get_obj_key(GaOutputModel),
            ],
            'input': [
                self._get_obj_key(GaInputModel),
                self._get_obj_key(GaInputDevice),
            ],
        }

    def get(self) -> tuple:
        """
        Pulls new config from db and compares it to the currently loaded one.
        It will build a dict of thread-timers that need to be added/replaced/deleted by the service.
        """
        return self.any_changes, self._get_timer(), self.new_object_list, self.new_config_dict

    def _get_timer(self) -> dict:
        timer_updates = {
            'add': [],
            'remove': [],
        }

        fns_log(f'Reload - got any changes: {self.any_changes}', level=6)

        if self.any_changes:
            new_timers = get_timer(config_dict=self.new_object_list, system_tasks=False)
            changes = self._supply_changes()

            reload_condition = self._check_changes(changes=changes, check='condition')
            reload_output = self._check_changes(changes=changes, check='output')
            reload_input = self._check_changes(changes=changes, check='input')

            # prepare some data to evaluate
            # output models/groups
            old_output_models = self.old_object_list[self._get_obj_key(GaOutputModel)]
            _remove_output_model = changes['remove'][self._get_obj_key(GaOutputModel)].copy()
            _remove_output_model.extend(changes['replace'][self._get_obj_key(GaOutputModel)])
            remove_output_model = [obj for obj in old_output_models if obj.object_id in _remove_output_model]

            _add_output_model = changes['add'][self._get_obj_key(GaOutputModel)].copy()
            _add_output_model.extend(changes['replace'][self._get_obj_key(GaOutputModel)])
            add_output_model = [obj for obj in self.new_object_list[self._get_obj_key(GaOutputModel)] if obj.object_id in _add_output_model]

            # output devices
            old_output_devices = self.old_object_list[self._get_obj_key(GaOutputDevice)].copy()

            _remove_output_device = changes['remove'][self._get_obj_key(GaOutputDevice)].copy()
            _remove_output_device.extend(changes['replace'][self._get_obj_key(GaOutputDevice)])
            remove_output_device = [obj for obj in old_output_devices if obj.object_id in _remove_output_device]
            remove_output_device.extend([member for parent in remove_output_model for member in parent.member_list])  # all children of this model must be replaced because of setting inheritance
            remove_output_device = set(remove_output_device)

            _add_output_device = changes['add'][self._get_obj_key(GaOutputDevice)].copy()
            _add_output_device.extend(changes['replace'][self._get_obj_key(GaOutputDevice)])
            add_output_device = [obj for obj in self.new_object_list[self._get_obj_key(GaOutputDevice)] if obj.object_id in _add_output_device]
            add_output_device.extend([member for parent in add_output_model for member in parent.member_list])  # all children of this model must be replaced because of setting inheritance
            add_output_device = set(add_output_device)

            # input models/devices
            _add_input_model = changes['add'][self._get_obj_key(GaInputModel)].copy()
            _add_input_model.extend(changes['replace'][self._get_obj_key(GaInputModel)])

            _add_input_device = changes['add'][self._get_obj_key(GaInputDevice)].copy()
            _add_input_device.extend(changes['replace'][self._get_obj_key(GaInputDevice)])

            add_input = {
                self._get_obj_key(GaInputModel): [obj for obj in self.new_object_list[self._get_obj_key(GaInputModel)] if obj.object_id in _add_input_model],
                self._get_obj_key(GaInputDevice): [obj for obj in self.new_object_list[self._get_obj_key(GaInputDevice)] if obj.object_id in _add_input_device]
            }

            # simple additions
            fns_log(f"Reload - additions: {changes['add']}", level=6)
            if reload_condition:
                timer_updates['add'].extend([timer for timer in new_timers if isinstance(timer, GaConditionGroup)])

            if reload_input:
                for key in self.reload_categories['input']:
                    if len(changes['add'][key]) > 0:
                        timer_updates['add'].extend([obj for obj in add_input[key] if obj.object_id in changes['add'][key]])

            # replacement and deletions => we sometimes have to link new instances with existing ones
            fns_log(f"Reload - replacements: {changes['replace']}", level=6)
            fns_log(f"Reload - removal: {changes['remove']}", level=6)
            for timer in self.old_timers:
                if reload_condition and isinstance(timer, GaConditionGroup):
                    # if condition changed => update the condition
                    timer_updates['remove'].append(timer)

                if reload_input and isinstance(timer, (GaInputDevice, GaInputModel)):
                    # if a input changed => replace the input
                    key = self._get_obj_key(type(timer))

                    if len(changes['remove'][key]) > 0 or len(changes['replace'][key]) > 0:
                        if timer.object_id in changes['remove'][key] or timer.object_id in changes['replace'][key]:
                            timer_updates['remove'].append(timer)

                    if len(changes['replace'][key]) > 0:
                        try:
                            timer_updates['add'].append([obj for obj in add_input[key] if obj.object_id == timer.object_id][0])

                        except IndexError:
                            # if this model should not be replaced it will not be matched
                            pass

                if reload_output and not reload_condition and isinstance(timer, GaConditionGroup):
                    # if a output changed => check all conditions for links to it and update them
                    # add new 'versions' of output devices and models to the condition lists
                    fns_log(f"Reload - updating outputs of condition {timer}", level=7)

                    for new_model in add_output_model:
                        try:
                            old_model = [old_model for old_model in old_output_models if old_model.object_id == new_model.object_id][0]
                            if old_model in timer.output_group_list:
                                fns_log(f"Reload - updating output {old_model} liked to condition {timer}", level=7)
                                timer.output_group_list.append(new_model)

                                if old_model.object_id in remove_output_model:
                                    timer.output_group_list.remove(old_model)
                                    remove_output_model.remove(old_model.object_id)
                                    del old_model

                        except IndexError:
                            # if this model should not be replaced it will not be matched
                            continue

                    for new_device in add_output_device:
                        try:
                            old_device = [old_device for old_device in old_output_devices if old_device.object_id == new_device.object_id][0]
                            if old_device in timer.output_object_list:
                                fns_log(f"Reload - updating output {old_device} liked to condition {timer}", level=7)
                                timer.output_object_list.append(new_device)

                                if old_device.object_id in remove_output_device:
                                    timer.output_object_list.remove(old_device)
                                    remove_output_device.remove(old_device.object_id)
                                    del old_device

                        except IndexError:
                            # if this model should not be replaced it will not be matched
                            continue

                    # remove the old 'versions' of output devices and models from condition lists
                    for old_model in remove_output_model:
                        if old_model in timer.output_group_list:
                            timer.output_group_list.remove(old_model)
                            del old_model

                    for old_device in remove_output_device:
                        if old_device in timer.output_object_list:
                            timer.output_object_list.remove(old_device)
                            del old_device

        fns_log(f'Reload - got timer changes: {timer_updates}', level=6)
        return timer_updates

    @staticmethod
    def _get_obj_key(obj):
        for key, value in blueprint_dict.items():
            if obj == value:
                return key

    def _check_changes(self, changes: dict, check: str) -> bool:
        result = False

        for key in self.reload_categories[check]:
            if changes['changed'][key]:
                result = True
                break

        fns_log(f'Reload - got changes for type {check}: {result}', level=6)
        return result

    def _supply_changes(self) -> dict:
        changes = {
            'add': {},
            'replace': {},
            'remove': {},
            'changed': {},
        }

        for key, supply_data in self.new_config_dict.items():
            _add = []
            _replace = []
            _remove = []
            _old_supply_data = self.old_config_dict[key]

            for _id, data in supply_data.items():
                if _id not in _old_supply_data:
                    _add.append(_id)

                elif data != _old_supply_data[_id]:
                    _replace.append(_id)

            for _id in _old_supply_data.keys():
                if _id not in supply_data:
                    _remove.append(_id)

            changes['add'][key] = _add
            changes['replace'][key] = _replace
            changes['remove'][key] = _remove

            if len(_add) > 0 or len(_replace) > 0 or len(_remove) > 0:
                changes['changed'][key] = True

            else:
                changes['changed'][key] = False

        fns_log(f'Reload - config raw changes: {changes}', level=8)
        return changes

    def _any_change(self) -> bool:
        new_json = json_dumps(self.new_config_dict, sort_keys=True, default=str)
        old_json = json_dumps(self.old_config_dict, sort_keys=True, default=str)

        if new_json == old_json:
            return False

        return True
