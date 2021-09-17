# creates condition group/object instances

from core.factory import config
from core.factory.forge.blueprint import blueprint_dict
from core.factory.forge.condition.link import Go as ConditionLink
from core.factory.forge.condition.match import Go as ConditionMatch
from core.factory.forge.condition.group import Go as ConditionGroup
from core.factory.forge.condition.match import GoSpecial as ConditionMatchSpecial
from core.utils.debug import log


class Go:
    def __init__(self, supply_data: dict, factory_data=None):
        self.supply_data = supply_data

    def get(self) -> dict:
        # {
        #     object_condition_match: [instance_list],
        #     object_condition_specialmatch: [instance_list],
        #     object_condition_link: [instance_list],
        #     group_condition: [instance_list]
        # }

        log(f'Building condition objects (all)', level=8)

        output = {}

        _config = {
            config.KEY_OBJECT_CONDITION_MATCH: ConditionMatch,
            config.KEY_OBJECT_CONDITION_MATCH_SPECIAL: ConditionMatchSpecial,
            config.KEY_OBJECT_CONDITION_LINK: ConditionLink,
            config.KEY_GROUP_CONDITION: ConditionGroup,
        }

        for key, factory in _config.items():
            output[key] = factory(
                blueprint=blueprint_dict[key],
                supply_list=self.supply_data[key],
            ).get()

        return output
