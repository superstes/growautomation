from core.factory import config
from core.factory.forge.blueprint import blueprint_dict
from core.factory.forge.system.controller import Go as ControllerFactory
from core.factory.forge.system.task import Go as TaskFactory
from core.utils.debug import log


class Go:
    def __init__(self, supply_data: dict, factory_data=None):
        self.supply_data = supply_data

        self.key_object_controller = config.KEY_OBJECT_CONTROLLER
        self.key_object_task = config.KEY_OBJECT_TASK

    def get(self) -> dict:
        # {
        #     object_controller: [instance_list],
        #     object_task: [instance_list],
        # }

        log(f'Building system objects (all)', level=8)

        output_dict = {
            self.key_object_controller: ControllerFactory(
                blueprint=blueprint_dict[self.key_object_controller],
                parent=blueprint_dict[config.KEY_GROUP_CONTROLLER](),
                # parent is only used for inheritance of settings -> will not be needed after controller object creation
                supply_list=self.supply_data[self.key_object_controller],
            ).get(),

            self.key_object_task: TaskFactory(
                blueprint=blueprint_dict[self.key_object_task],
                supply_list=self.supply_data[self.key_object_task],
            ).get()
        }

        return output_dict
