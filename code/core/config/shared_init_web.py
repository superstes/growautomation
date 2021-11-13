from inspect import getmembers, ismethod

from core.config import shared as config


class PseudoConfigObject:
    pass


def _create_pseudo_config(source_obj):
    attributes = {}

    for attr in getmembers(source_obj):
        if not attr[0].startswith('_'):
            value = attr[1]

            if not ismethod(value):
                # transform django values to the ones we would expect to get from the db
                #   could be done in reverse (in the factory) in the future.. would probably be a cleaner way to handle this
                if type(value) == bool:
                    if value:
                        value = 1
                    else:
                        value = 0

                attributes[attr[0]] = value

    obj = PseudoConfigObject()
    for key, value in attributes.items():
        setattr(obj, key, value)

    return obj


def init(agent_obj, server_obj):
    try:
        _ = config.AGENT.path_root
        _ = config.SERVER.security

    except (AttributeError, NameError):
        config.init()
        config.AGENT = _create_pseudo_config(agent_obj)
        config.SERVER = _create_pseudo_config(server_obj)
