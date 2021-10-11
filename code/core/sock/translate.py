# will translate the api-call received from the socket-server to an actual action

from re import match as regex_match

from core.utils.debug import log
from core.config.socket import PACKAGE_PATH_SEPARATOR
from core.config import shared as config
from core.factory import config as factory_config


class Route:
    def __init__(self, parsed: dict):
        self.path = parsed['path'].split(PACKAGE_PATH_SEPARATOR)[0].split('.')
        self.data = parsed['data']
        self.status = None
        try:
            self.path_main = f'{self.path[0]}.{self.path[1]}'
            self.path_type = self.path[2]
            self.path_subtype = self.path[3]
            self.path_id = int(self.path[4])

        except (TypeError, IndexError):
            log(f'Router did not get all expected arguments!', level=3)
            raise IndexError

    def go(self) -> tuple:
        mapping = {
            'device\\..*': self._device,
            'group\\.(input|output|connection)': self._device,
        }

        if self.path_main == 'ga.core':
            check = f'{self.path_type}.{self.path_subtype}'
            for match, goto in mapping.items():
                if regex_match(match, check) is not None:
                    return goto(), self.status

            log('No route matched!', level=5)

        else:
            log("Wrong api root-path supplied => should be 'ga.core'", level=4)

        return False, self.status

    def _device(self) -> bool:
        from core.device.output.main import Go as Output
        from core.device.input.main import Go as Input
        mapping = {
            'device': {
                'input': factory_config.KEY_OBJECT_INPUT,
                'output': factory_config.KEY_OBJECT_OUTPUT,
                'connection': factory_config.KEY_OBJECT_CONNECTION,
            },
            'group': {
                'input': factory_config.KEY_GROUP_INPUT,
                'output': factory_config.KEY_GROUP_OUTPUT,
                'connection': factory_config.KEY_GROUP_CONNECTION,
            }
        }

        action = self.data
        key = mapping[self.path_type][self.path_subtype]
        result = None

        # check state of device => stateful or -less => active and/or locked
        #   stateless => start is the only option => get lock and start
        #   stateful:
        #     if active and start => do nothing (add force if it should be stopped and restarted ?)
        #     if inactive and start => start
        #     if active and stop => only run reversal

        for obj in config.CONFIG[key]:
            if getattr(obj, factory_config.CORE_ID_ATTRIBUTE) == self.path_id:
                log(f'Executing {action} for {self.path_subtype}-{self.path_type} with id {self.path_id}', level=6)

                if self.path_subtype == 'output':
                    if action == 'start':
                        if getattr(obj, 'locked') or getattr(obj, 'active'):
                            log(f"Unable to start output-{self.path_type} '{obj}' since it is already active!", level=3)

                        else:
                            result = Output(instance=obj, action=action, manually=True).start()

                    elif action == 'stop':
                        result = Output(instance=obj, action=action, manually=True).start()

                    else:
                        log(f"Got an unsupported action '{action}' for {self.path_subtype}-device!", level=4)

                    if self.status is None:
                        self.status = getattr(obj, 'active')

                else:  # if input or connection
                    if action == 'start':
                        result = Input(instance=obj, manually=True).start()

                    else:
                        log(f"Got an unsupported action '{action}' for {self.path_subtype}-device!", level=4)

        if result is not None:
            if result:
                log(f"Execution of {self.path_subtype}-device with id {self.path_id} was successful!", level=6)
            else:
                log(f"Execution of {self.path_subtype}-device with id {self.path_id} failed!", level=3)

            return result

        return False
