from core.factory import config
from core.factory.forge.blueprint import blueprint_dict
from core.factory.forge.member import Go as Member
from core.factory.forge.device.generic import Go as GenericDeviceFactory


class Go:
    def __init__(self, supply_dict: dict):
        self.supply_dict = supply_dict

        self.key_object_connection = config.KEY_OBJECT_CONNECTION

    def get(self) -> dict:
        # {
        #     object_connection: [instance_list],
        #     object_input: [instance_list],
        #     group_connection: [instance_list],
        #     object_output: [instance_list],
        #     group_input: [instance_list],
        #     group_output: [instance_list],
        # }

        output_dict = {}

        device_config_list = [
            {'bp': GenericDeviceFactory, 'ok': self.key_object_connection, 'gk': config.KEY_GROUP_CONNECTION},
            {'bp': GenericDeviceFactory, 'ok': config.KEY_OBJECT_INPUT, 'gk': config.KEY_GROUP_INPUT},
            {'bp': GenericDeviceFactory, 'ok': config.KEY_OBJECT_OUTPUT, 'gk': config.KEY_GROUP_OUTPUT},
        ]

        for device_config in device_config_list:
            _group_list = device_config['bp'](
                blueprint=blueprint_dict[device_config['gk']],
                supply_list=self.supply_dict[device_config['gk']],
            ).get_model()

            if self.key_object_connection in output_dict:
                _downlink_list = output_dict[self.key_object_connection]
            else:
                _downlink_list = None

            _object_list = device_config['bp'](
                blueprint=blueprint_dict[device_config['ok']],
                supply_list=self.supply_dict[device_config['ok']],
            ).get_device(
                parent_list=_group_list,
                downlink_list=_downlink_list,
            )

            _group_list = Member(
                object_list=_group_list,
                member_list=_object_list,
                member_attribute=config.CORE_MEMBER_ATTRIBUTE,
            ).add()

            output_dict[device_config['gk']] = _group_list
            output_dict[device_config['ok']] = _object_list

        return output_dict
