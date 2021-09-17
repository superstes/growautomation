from core.config import shared as shared_vars


def init(controller_obj):
    try:
        _ = shared_vars.SYSTEM.path_root

    except (AttributeError, NameError):
        shared_vars.init()
        shared_vars.SYSTEM = controller_obj
