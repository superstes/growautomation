

from core.config.object.core.core import *
from core.config.object.core.controller import *
from core.config.object.device.output import *
from core.config.object.device.input import *
from core.config.object.device.connection import *
from core.config.object.setting.condition import *
from core.config.object.group.group import *
from core.config.object.group.area import *

import json



device_typeid_mapping = {
    0: GaCoreDevice, 1: GaControllerDevice, 11: GaSensorDevice, 12: GaActorDevice, 13: GaDownlinkDevice
}
model_typeid_mapping = {
    0: GaCoreModel, 1: GaControllerModel, 11: GaSensorModel, 12: GaActorModel, 13: GaDownlinkModel
}


#######################################################################################################################
# model objects

model_instance_dict = {}
model_device_mapping_dict = {}
for model_id, config in json.loads(get_model_data()).items():
    print(config['name'])
    model_object = model_typeid_mapping[config['model_type']]
    model_instance = model_object(object_id=model_id, **config)
    model_instance_dict[model_id] = model_instance
    model_device_mapping_dict[model_instance] = config['child_list']

#######################################################################################################################
# device objects

device_data_dict = json.loads(get_device_data())

device_instance_dict = {}
for model_instance, child_list in model_device_mapping_dict.items():
    for device_id in child_list:
        try:
            config = device_data_dict[str(device_id)]
        except KeyError:
            print("Device key '%s' not found in device_data_dict '%s'" % (device_id, device_data_dict.keys()))
            continue
        print(config['name'])
        device_object = device_typeid_mapping[model_instance.model_type]
        device_instance_dict[device_id] = device_object(model_instance=model_instance, object_id=device_id, **config)


#######################################################################################################################
# tmp debug
print('###########################-Models-###########################')
for model_id, model in model_instance_dict.items():
    print("Model id: %s" % model_id)
    print("Model object: %s\n" % model.__repr__())

print('###########################-Devices-###########################')

for device_id, device in device_instance_dict.items():
    print("Device id: %s" % device_id)
    print("Enabled: %s" % device.is_enabled)
    print("Device enabled: %s" % device.device_enabled)
    print("Model enabled: %s" % device.model_instance.is_enabled)
    print("Device object: %s\n" % device.__repr__())


