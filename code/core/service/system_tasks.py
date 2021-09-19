from core.config.object.core.task import SystemTask

from core.sock.connect import Server as SocketServer


def get_tasks() -> list:
    return [
        SystemTask(
            name='Socket Server',
            description='Server to receive commands from other clients or parts of the software',
            execute=SocketServer().run,
            setting_dict={'timer': 10},
            object_id=1,
        ),
    ]

