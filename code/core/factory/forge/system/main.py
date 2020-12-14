from core.factory import config
from core.factory.forge.blueprint import blueprint_dict
from core.factory.forge.system.controller import Go as ControllerFactory
from core.factory.forge.system.timer import Go as TimerFactory


class Go:
    def __init__(self, supply_dict: dict):
        self.supply_dict = supply_dict

        self.key_object_controller = config.KEY_OBJECT_CONTROLLER
        self.key_group_controller = config.KEY_GROUP_CONTROLLER
        self.key_object_timer = config.KEY_OBJECT_TIMER

    def get(self) -> dict:
        # {
        #     object_controller: [instance_list],
        #     object_timer: [instance_list],
        # }

        output_dict = {

            self.key_object_controller: ControllerFactory(
                blueprint=blueprint_dict[self.key_object_controller],
                parent=blueprint_dict[self.key_group_controller](),
                # parent is only used for inheritance of settings -> will not be needed after controller object creation
                supply_list=self.supply_dict[self.key_object_controller],
            ).get(),

            self.key_object_timer: TimerFactory(
                blueprint=blueprint_dict[self.key_object_timer],
                supply_list=self.supply_dict[self.key_object_timer],
            ).get()

        }

        return output_dict
