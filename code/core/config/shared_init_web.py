from core.config import shared as config


def init(agent_obj, server_obj):
    try:
        _ = config.AGENT.path_root
        _ = config.SERVER.security

    except (AttributeError, NameError):
        config.init()
        config.AGENT = agent_obj
        config.SERVER = server_obj
