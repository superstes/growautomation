from core.factory import config
from core.factory.forge.blueprint import blueprint_dict
from core.factory.forge.device.generic import Go as GenericDeviceFactory
from core.utils.debug import log
from core.config.object.data.db import GaDataDb
from core.config.db.template import DEVICE_TMPL


class Go:
    def __init__(self, supply_data: dict, factory_data=None):
        self.supply_data = supply_data
        self.database = GaDataDb()

    def get(self) -> dict:
        # {
        #     object_connection: [instance_list],
        #     object_input: [instance_list],
        #     group_connection: [instance_list],
        #     object_output: [instance_list],
        #     group_input: [instance_list],
        #     group_output: [instance_list],
        # }

        log('Building device objects (all)', level=8)

        output_dict = {}

        device_config_list = [
            {'bp': GenericDeviceFactory, 'ok': config.KEY_OBJECT_CONNECTION, 'gk': config.KEY_GROUP_CONNECTION},
            {'bp': GenericDeviceFactory, 'ok': config.KEY_OBJECT_INPUT, 'gk': config.KEY_GROUP_INPUT},
            {'bp': GenericDeviceFactory, 'ok': config.KEY_OBJECT_OUTPUT, 'gk': config.KEY_GROUP_OUTPUT},
        ]

        update_states = {
            config.KEY_OBJECT_OUTPUT: {'attribute': 'state', 'query': DEVICE_TMPL['output']['state']['get'], 'value': 1, 'set_to': True},
        }

        for device_config in device_config_list:
            output_dict[device_config['gk']] = device_config['bp'](
                blueprint=blueprint_dict[device_config['gk']],
                supply_data=self.supply_data[device_config['gk']],
            ).get_model()

            output_dict[device_config['ok']] = device_config['bp'](
                blueprint=blueprint_dict[device_config['ok']],
                supply_data=self.supply_data[device_config['ok']],
            ).get_device()

            if device_config['ok'] in update_states:
                update = update_states[device_config['ok']]
                attribute = update['attribute']

                for device in output_dict[device_config['ok']]:
                    result = self.database.get(update['query'] % device.object_id)

                    if result is not None and len(result) > 0:
                        db_value = result[0]['active']

                        if db_value == update['value']:
                            log(f"Setting {attribute} of device {device.name} to value from db!", level=5)

                            if 'set_to' in update:
                                setattr(device, attribute, update['set_to'])

                            else:
                                setattr(device, attribute, db_value)

        return output_dict
