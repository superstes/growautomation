from core.factory import config

from core.config.object.device.input import GaInputDevice
from core.config.object.device.input import GaInputModel
from core.config.object.device.output import GaOutputDevice
from core.config.object.device.output import GaOutputModel
from core.config.object.device.connection import GaConnectionDevice
from core.config.object.device.connection import GaConnectionModel
from core.config.object.core.controller import GaControllerDevice
# from core.config.object.core.controller import GaControllerModel
# from core.config.object.core.timer import GaTimerDevice
# from core.config.object.core.timer import GaTimerModel
from core.config.object.setting.condition import GaConditionMatch
from core.config.object.setting.condition import GaConditionGroup
from core.config.object.setting.condition import GaConditionLink

blueprint_dict = {
    config.KEY_OBJECT_INPUT: GaInputDevice,
    config.KEY_OBJECT_OUTPUT: GaOutputDevice,
    config.KEY_OBJECT_CONNECTION: GaConnectionDevice,
    config.KEY_OBJECT_CONDITION_LINK: GaConditionLink,
    config.KEY_OBJECT_CONDITION_MATCH: GaConditionMatch,
    config.KEY_OBJECT_CONTROLLER: GaControllerDevice,
    config.KEY_GROUP_INPUT: GaInputModel,
    config.KEY_GROUP_OUTPUT: GaOutputModel,
    config.KEY_GROUP_CONNECTION: GaConnectionModel,
    config.KEY_GROUP_CONDITION: GaConditionGroup,
}
