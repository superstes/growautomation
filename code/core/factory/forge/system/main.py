from core.factory import config
from core.config.object.core.system import GaServer, GaAgent
from core.utils.debug import log, censor


class Go:
    def __init__(self, supply_data: dict, factory_data=None):
        self.supply_data = supply_data

        self.key_object_controller = config.KEY_OBJECT_AGENT
        self.key_object_task = config.KEY_OBJECT_TASK

    def get(self) -> dict:
        # {
        #     object_controller: [instance_list],
        #     object_task: [instance_list],
        # }

        log(f'Building system objects (all)', level=8)
        output_dict = {}

        _config = {
            config.KEY_OBJECT_SERVER: GaServer,
            config.KEY_OBJECT_AGENT: GaAgent,
        }

        for key, blueprint in _config.items():
            # todo: for multi-agent support we must get the right agent config
            try:
                output_dict[key] = [blueprint(
                    setting_dict=self.supply_data[key][1][config.SUPPLY_KEY_SETTING_DICT],
                    object_id=self.supply_data[key][1][config.DB_ALL_KEY_ID],
                    name=self.supply_data[key][1][config.DB_ALL_KEY_NAME],
                    description=self.supply_data[key][1][config.DB_ALL_KEY_DESCRIPTION],
                )]

            except (IndexError, KeyError) as error:
                log(f"Factory wasn't able to pull {key}-data from database! Make sure the configuration exists!", level=1)
                raise KeyError(censor(error))

        # output_dict.update({
        #     self.key_object_task: TaskFactory(
        #         blueprint=blueprint_dict[self.key_object_task],
        #         supply_data=self.supply_data[self.key_object_task],
        #     ).get()
        # })

        return output_dict
