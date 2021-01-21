# either
#   starts input/connection script and pulls data for insertion into db
# or
#   starts output script


from core.utils.process import subprocess
from core.config import shared as shared_vars
from core.utils.debug import debugger
from core.utils.debug import Log
from core.device import lock
from core.config.object.device.input import GaInputDevice
from core.config.object.device.connection import GaConnectionDevice

from json import dumps as json_dumps
from json import loads as json_loads
from json import JSONDecodeError


class Go:
    INPUT_CATEGORY = 'input'
    CONNECTION_CATEGORY = 'connection'
    INPUT_DATA_KEY = 'data'
    OUTPUT_CATEGORY = 'output'
    SCRIPT_SUBPATH = "device/%s"

    def __init__(self, instance, category: str, reverse: bool = False, nested_instance=None):
        self.instance = instance
        self.category = category
        self.reverse = reverse
        self.nested_instance = nested_instance
        self.logger = Log()

    def start(self) -> (str, None):
        if lock.get(instance=self.instance):
            result = self._execute()

            lock.remove(instance=self.instance)
            debugger("device-process | start | instance \"%s\" result \"%s\"" % (self.instance.name, result))

            if self.category in [self.INPUT_CATEGORY, self.CONNECTION_CATEGORY]:
                try:
                    data = json_loads(result)
                    return data[self.INPUT_DATA_KEY]

                except (KeyError, JSONDecodeError) as error:
                    self.logger.write("Unable decode received data; error: \"%s\"" % error)
                    return None

            else:
                return result

        else:
            return None

    def _execute(self):
        if isinstance(self.instance, GaInputDevice):
            config_dict = {
                'connection': self.instance.connection,
            }

        elif isinstance(self.instance, GaConnectionDevice):
            try:
                try:
                    connection = json_loads(self.instance.connection)

                except (TypeError, JSONDecodeError):
                    connection_json = self.instance.connection.replace("'", "\"")
                    connection = json_loads(connection_json)

            except (TypeError, JSONDecodeError):
                connection = self.instance.connection

            config_dict = {
                'connection': connection,
                'downlink_pin': self.nested_instance.connection
            }

        else:
            config_dict = {}

        script = self.instance.script
        script_arg = self.instance.script_arg
        script_bin = self.instance.script_bin

        if script in [None, '', 'None'] or script_bin in [None, '', 'None']:  # it should only be possible to be NoneType-None
            self.logger.write("No script or binary provided to execute for device \"%s\"" % self.instance.name)
            return None

        if self.category == self.OUTPUT_CATEGORY:
            reverse = False

            if self.instance.reverse and self.instance.active and self.reverse:
                reverse = True
                script = self.instance.reverse_script
                script_arg = self.instance.reverse_script_arg
                script_bin = self.instance.reverse_script_bin

        command = "%s %s/%s/%s \"%s\" \"%s\"" % (
            script_bin,
            shared_vars.SYSTEM.path_root,
            self.SCRIPT_SUBPATH % self.category,
            script,
            script_arg,
            str(json_dumps(config_dict)).replace("\"", "\\\"")
        )

        result, error = subprocess(command=command, out_error=True)

        if error not in [None, '']:
            self.logger.write("An error occurred while processing device \"%s\": \"%s\"" % (self.instance.name, error))

        if self.category == self.OUTPUT_CATEGORY:
            if error is None:
                result = True

                if reverse:
                    self.instance.active = False
                elif self.instance.reverse and not self.instance.active:
                    self.instance.active = True

            else:
                result = False

        return result
