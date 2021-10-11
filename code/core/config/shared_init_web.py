from core.config import shared as config


def init(controller_obj):
    try:
        _ = config.SYSTEM.path_root

    except (AttributeError, NameError):
        config.init()
        config.SYSTEM = controller_obj
