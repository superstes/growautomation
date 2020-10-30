# defines which objects to create
# returns a dict that links the objects to create to grouptype-ids


class Go:
    GROUPTYPE_CATEGORY_ARG = 'TypeCategory'
    GROUPTYPE_OBJECT_ARG = 'TypeName'

    def __init__(self, type_dict: dict):
        self.type_dict = type_dict
        self.category_list = []
        self.object_list = []
        self.object_mapping_dict = {}
        # { typeid: {subcategory: {model: object, object: object} } }
        self.output_dict = {}

    def get(self) -> dict:
        for type_id, config_dict in self.type_dict.items():
            self.category_list.append(config_dict[self.GROUPTYPE_CATEGORY_ARG])
            self.object_list.append(config_dict[self.GROUPTYPE_OBJECT_ARG])

        self._blueprint_device()
        self._blueprint_core()

        return self.object_mapping_dict

    def _add_mapping(self, model, obj, map_value: str) -> None:
        for key, value in self.type_dict.items():
            if value[self.GROUPTYPE_OBJECT_ARG] == map_value:
                map_id = key

        try:
            if map_id not in self.object_mapping_dict:
                self.object_mapping_dict[map_id] = {}

            self.object_mapping_dict[map_id] = {'model': model, 'object': obj}
        except KeyError:
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

    def _blueprint_core_controller(self) -> None:
        from core.config.object.core.controller import GaControllerDevice
        from core.config.object.core.controller import GaControllerModel

        self._add_mapping(model=GaControllerModel, obj=GaControllerDevice, map_value='controller')
