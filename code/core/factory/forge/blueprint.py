from core.factory import config

from core.config.object.device.input import GaInputDevice, GaInputModel
from core.config.object.device.output import GaOutputDevice, GaOutputModel
from core.config.object.device.connection import GaConnectionDevice, GaConnectionModel
from core.config.object.core.controller import GaControllerDevice, GaControllerModel
from core.config.object.core.task import GaTaskDevice
from core.config.object.setting.condition import GaConditionMatch, GaConditionGroup, GaConditionLink, GaConditionMatchSpecial
from core.config.object.group.main import GaAreaGroup

blueprint_dict = {
    config.KEY_OBJECT_INPUT: GaInputDevice,
    config.KEY_OBJECT_OUTPUT: GaOutputDevice,
    config.KEY_OBJECT_CONNECTION: GaConnectionDevice,
    config.KEY_OBJECT_CONDITION_LINK: GaConditionLink,
    config.KEY_OBJECT_CONDITION_MATCH: GaConditionMatch,
    config.KEY_OBJECT_CONDITION_MATCH_SPECIAL: GaConditionMatchSpecial,
    config.KEY_OBJECT_CONTROLLER: GaControllerDevice,
    config.KEY_OBJECT_TASK: GaTaskDevice,
    config.KEY_GROUP_CONTROLLER: GaControllerModel,
    config.KEY_GROUP_INPUT: GaInputModel,
    config.KEY_GROUP_OUTPUT: GaOutputModel,
    config.KEY_GROUP_CONNECTION: GaConnectionModel,
    config.KEY_GROUP_CONDITION: GaConditionGroup,
    config.KEY_GROUP_AREA: GaAreaGroup,
}
