# will translate the api-call received from the socket-server to an actual action

from core.utils.debug import log
from core.config.socket import PACKAGE_PATH_SEPARATOR


class Route:
    # interpret path (and data[?])
    def __init__(self, parsed: dict):
        self.path = parsed['path'].split(PACKAGE_PATH_SEPARATOR)[0].split('.')
        self.data = parsed['data']
        self.MAPPING = {
            'device': self._device,
        }

    def go(self) -> bool:
        if f'{self.path[0]}.{self.path[1]}' == 'ga.core':
            try:
                return self.MAPPING[self.path[2]]()

            except KeyError:
                log('Wrong api main-path supplied', level=4)

        else:
            log("Wrong api root-path supplied => should be 'ga.core'", level=4)

        return False

    def _device(self) -> bool:
        try:
            device_type = self.path[3]
            device_id = self.path[4]
            action = self.data

        except IndexError:
            log(f'Either device-type or device-id were not supplied!', level=4)
            return False

        log(f'Executing {action} for {device_type}-device #{device_id}', level=6)

        return True
