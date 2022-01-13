from django.db.utils import OperationalError, ProgrammingError

from core.utils.process import subprocess
from core.utils.debug import web_log

from ..models import SystemServerModel, SystemAgentModel
from ..models import ObjectInputModel, ObjectOutputModel, ObjectConnectionModel
from ..models import GroupInputModel, GroupOutputModel, GroupConnectionModel
from ..models import MemberInputModel, MemberOutputModel, MemberConnectionModel

DEVICE_TYPES = [ObjectInputModel, ObjectOutputModel, ObjectConnectionModel]
ALL_DEVICE_TYPES = [GroupInputModel, GroupOutputModel, GroupConnectionModel]
ALL_DEVICE_TYPES.extend(DEVICE_TYPES)


class PseudoServerAgent:
    # needed for migrations on the agent/server models and setup (no system tables exist or are unusable)
    def __init__(self):
        self.subprocess_timeout = 60
        self.security = 1
        self.version = 'DATABASE ERROR'
        self.version_detail = '| CHECK SCHEMA'


def get_server() -> (SystemServerModel, None):
    try:
        return SystemServerModel.objects.all()[0]

    except IndexError:
        return None

    except (OperationalError, ProgrammingError):
        return PseudoServerAgent()


def get_agent(name: str = None) -> (SystemAgentModel, None):
    try:
        if name is None:
            return SystemAgentModel.objects.all()[0]

        else:
            return SystemAgentModel.objects.filter(name=name)[0]

    except IndexError:
        return None

    except (OperationalError, ProgrammingError):
        return PseudoServerAgent()


def get_agent_config(setting: str):
    return getattr(get_agent(), setting)


def get_server_config(setting: str):
    return getattr(get_server(), setting)


def get_script_dir(typ) -> str:
    path_root = get_agent_config(setting='path_root')
    return f"{path_root}/device/{typ.lower()}"


def init_core_config():
    from core.config.shared_init_web import init
    init(agent_obj=get_agent(), server_obj=get_server())


def web_subprocess(command: str, out_error: bool = False) -> str:
    init_core_config()
    return subprocess(command=command, out_error=out_error, logger=web_log)


def get_instance_from_id(typ, obj: (str, int), force_id: bool = False):
    if obj in [None, '', 'None'] or type(obj) not in (str, int):
        return None

    for check_obj in typ.objects.all():
        if type(obj) == str:
            if force_id:
                if check_obj.id == int(obj):
                    return check_obj

            else:
                if check_obj.name == obj:
                    return check_obj

        else:
            if check_obj.id == obj:
                return check_obj

    return None


def get_device_parent(child_obj):
    parent = None
    member_link_list = None

    if isinstance(child_obj, ObjectInputModel):
        member_link_list = MemberInputModel.objects.all()

    elif isinstance(child_obj, ObjectOutputModel):
        member_link_list = MemberOutputModel.objects.all()

    elif isinstance(child_obj, ObjectConnectionModel):
        member_link_list = MemberConnectionModel.objects.all()

    if member_link_list is not None:
        for link in member_link_list:
            if link.obj == child_obj:
                parent = link.group
                break

    return parent


def get_device_parent_setting(child_obj: DEVICE_TYPES, setting: str):
    if not isinstance(child_obj, tuple(DEVICE_TYPES)):
        return None

    parent = get_device_parent(child_obj)
    return getattr(parent, setting)


def member_pre_process(request, member_data_dict: dict, member_config: dict):
    output = {}
    member_view_active = False

    if 'list_member' in request.GET:
        member_view_active = request.GET['list_member']

        for key, data in member_data_dict.items():
            group_key = member_config[key]['group_key']
            member_key = member_config[key]['member_key']

            for member in data:
                member_group = getattr(member, group_key)
                member_repr = getattr(member, member_key)
                if member_group.name == member_view_active and member_repr is not None:
                    if key in output:
                        output[key].append(member)

                    else:
                        output[key] = [member]

    if member_view_active is False:
        return member_view_active, member_data_dict
    else:
        return member_view_active, output


def error_formatter(form_error, fallback: str = 'Failed to save form') -> str:
    try:
        return str(list(form_error.as_data().values())[0][0]).replace("['", '').replace("']", '')

    except IndexError:
        return fallback
