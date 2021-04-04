from core.factory import config
from core.factory.forge.blueprint import blueprint_dict
from core.factory.forge.device.generic import Go as GenericDeviceFactory
from core.utils.debug import Log


class Go:
    def __init__(self, supply_data: dict, factory_data=None):
        self.supply_data = supply_data
        self.logger = Log()

    def get(self) -> dict:
        # {
        #     object_connection: [instance_list],
        #     object_input: [instance_list],
        #     group_connection: [instance_list],
        #     object_output: [instance_list],
        #     group_input: [instance_list],
        #     group_output: [instance_list],
        # }

        self.logger.write(f'Building device objects (all)', level=8)

        output_dict = {}

        device_config_list = [
            {'bp': GenericDeviceFactory, 'ok': config.KEY_OBJECT_CONNECTION, 'gk': config.KEY_GROUP_CONNECTION},
            {'bp': GenericDeviceFactory, 'ok': config.KEY_OBJECT_INPUT, 'gk': config.KEY_GROUP_INPUT},
            {'bp': GenericDeviceFactory, 'ok': config.KEY_OBJECT_OUTPUT, 'gk': config.KEY_GROUP_OUTPUT},
        ]

        for device_config in device_config_list:
            output_dict[device_config['gk']] = device_config['bp'](
                blueprint=blueprint_dict[device_config['gk']],
                supply_list=self.supply_data[device_config['gk']],
            ).get_model()

            output_dict[device_config['ok']] = device_config['bp'](
                blueprint=blueprint_dict[device_config['ok']],
                supply_list=self.supply_data[device_config['ok']],
            ).get_device()

        return output_dict
