# condition group processing

from core.config import shared as shared_vars
from core.config.object.setting.condition import GaConditionGroup


def get() -> list:
    return _get_main_groups(group_list=_get_groups())


def _get_groups() -> list:
    group_list = []

    for instance in shared_vars.CONFIG:
        if isinstance(instance, GaConditionGroup):
            group_list.append(instance)

    return group_list


def _get_main_groups(group_list: list) -> list:
    main_list = []

    for group in group_list:
        if group.main:
            main_list.append(group)

    return main_list
