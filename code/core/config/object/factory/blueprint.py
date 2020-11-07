# defines which objects to create
# returns a dict that links the objects to create to grouptype-ids

from core.config.object.factory.helper import factory as helper
from core.utils.debug import debugger
from core.utils.debug import Log


class Go:
    GROUPTYPE_CATEGORY_ARG = 'TypeCategory'
    GROUPTYPE_OBJECT_ARG = 'TypeName'

    def __init__(self, type_dict: dict):
        self.type_dict = type_dict
        self.category_list = []
        self.object_list = []
        self.object_mapping_dict = {}
        # {
        #     typeid: {
        #         subcategory: {model: obj, object: obj} -> default blueprints
        #     },
        #     typeid: {
        #         subcategory: {model: obj, object: obj, setting: obj}   -> settings blueprints
        #     }
        # }
        self.output_dict = {}

    def get(self) -> dict:
        for type_id, config_dict in self.type_dict.items():
            self.category_list.append(config_dict[self.GROUPTYPE_CATEGORY_ARG])
            self.object_list.append(config_dict[self.GROUPTYPE_OBJECT_ARG])

        self._blueprint_device()
        self._blueprint_core()
        self._blueprint_setting()

        return self.object_mapping_dict

    def _add_mapping(self, model, obj, map_value: str, setting=None) -> None:
        map_id = None

        for key, value in self.type_dict.items():
            if value[self.GROUPTYPE_OBJECT_ARG] == map_value:
                map_id = key
                break

        try:
            if setting is not None:
                self.object_mapping_dict[map_id] = {helper.BLUEPRINT_GROUP_KEY: model,
                                                    helper.BLUEPRINT_OBJECT_KEY: obj,
                                                    helper.BLUEPRINT_SETTING_KEY: setting}
            else:
                self.object_mapping_dict[map_id] = {helper.BLUEPRINT_GROUP_KEY: model,
                                                    helper.BLUEPRINT_OBJECT_KEY: obj}

        except KeyError:
            debugger("config-obj-factory-blueprint | _add_mapping | mapping value not in dict '%s'" % map_value)
            # log error or whatever -> mapping value not in type_dict (?)
            return None

    def _blueprint_device(self) -> None:
        if 'device' in self.category_list:
            if 'input' in self.object_list:
                self._blueprint_device_input()

            if 'output' in self.object_list:
                self._blueprint_device_output()

            if 'connection' in self.object_list:
                self._blueprint_device_connection()

    def _blueprint_device_input(self) -> None:
        from core.config.object.device.input import GaInputDevice
        from core.config.object.device.input import GaInputModel

        self._add_mapping(model=GaInputModel, obj=GaInputDevice, map_value='input')

    def _blueprint_device_output(self) -> None:
        from core.config.object.device.output import GaOutputDevice
        from core.config.object.device.output import GaOutputModel

        self._add_mapping(model=GaOutputModel, obj=GaOutputDevice, map_value='output')

    def _blueprint_device_connection(self) -> None:
        from core.config.object.device.connection import GaConnectionDevice
        from core.config.object.device.connection import GaConnectionModel

        self._add_mapping(model=GaConnectionModel, obj=GaConnectionDevice, map_value='connection')

    def _blueprint_core(self) -> None:
        if 'core' in self.category_list:
            if 'controller' in self.object_list:
                self._blueprint_core_controller()

            if 'timer' in self.object_list:
                self._blueprint_core_timer()

    def _blueprint_core_controller(self) -> None:
        from core.config.object.core.controller import GaControllerDevice
        from core.config.object.core.controller import GaControllerModel

        self._add_mapping(model=GaControllerModel, obj=GaControllerDevice, map_value='controller')

    def _blueprint_core_timer(self) -> None:
        from core.config.object.core.timer import GaTimerDevice
        from core.config.object.core.timer import GaTimerModel

        self._add_mapping(model=GaTimerModel, obj=GaTimerDevice, map_value='timer')

    def _blueprint_setting(self) -> None:
        if 'setting' in self.category_list:
            if 'condition' in self.object_list:
                self._blueprint_setting_condition()

    def _blueprint_setting_condition(self) -> None:
        from core.config.object.setting.condition import GaCondition
        from core.config.object.setting.condition import GaConditionGroup
        from core.config.object.setting.condition import GaConditionLink

        self._add_mapping(model=GaConditionGroup, obj=GaCondition, setting=GaConditionLink, map_value='condition')
