# either
#   starts input/connection script and pulls data for insertion into db
# or
#   starts output script

from core.utils.process import subprocess
from core.config import shared as shared_vars
from core.device.log import device_logger
from core.device import lock
from core.config.object.device.input import GaInputDevice
from core.config.object.device.output import GaOutputDevice
from core.config.object.device.connection import GaConnectionDevice

from json import dumps as json_dumps
from json import loads as json_loads
from json import JSONDecodeError
from datetime import datetime


class Go:
    INPUT_DATA_KEY = 'data'
    SCRIPT_SUBPATH = "device/%s"

    def __init__(self, instance, script_dir: str, reverse: bool = False, nested_instance=None):
        self.instance = instance
        self.reverse = reverse
        self.nested_instance = nested_instance
        self.logger = device_logger(addition=instance.name)
        self.script_dir = script_dir

    def start(self) -> (str, None, bool):
        # output:
        #   None -> Error
        #   False -> Fail-Sleep
        #   True -> successful output
        #   str/data -> successful input

        if self._fail_check():
            if lock.get(instance=self.instance):
                result = self._execute()

                lock.remove(instance=self.instance)
                self.logger.write(f"Device \"{self.instance.name}\" result \"{result}\"", level=6)

                if isinstance(self.instance, (GaInputDevice, GaConnectionDevice)):
                    if self.instance.fail_count == 0:
                        try:
                            data = json_loads(result)
                            return data[self.INPUT_DATA_KEY]

                        except (KeyError, JSONDecodeError) as error:
                            self.logger.write(f"Unable decode received data; error: \"{error}\"", level=2)
                            return None

                else:
                    return result

        else:
            return False

        return None

    def _fail_check(self):
        if self.instance.fail_sleep is not None:
            if datetime.now() < self.instance.fail_sleep:
                self.logger.write(f"Skipping execution of device \"{self.instance.name}\" since it has reached the max error threshold", level=4)
                self.logger.write(f"Device \"{self.instance.name}\" will be skipped until \"{self.instance.fail_sleep.strftime('%Y-%m-%d %H:%M:%S:%f')}\"", level=6)
                return False

        return True

    def _execute(self):
        if isinstance(self.instance, (GaInputDevice, GaOutputDevice)):
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

        params_dict = self._get_script_params()

        if params_dict is None or not self._reverse_check:
            return None

        command = "%s %s/%s/%s \"%s\" \"%s\"" % (
            params_dict['bin'],
            shared_vars.SYSTEM.path_root,
            self.SCRIPT_SUBPATH % self.script_dir,
            params_dict['script'],
            params_dict['arg'],
            str(json_dumps(config_dict)).replace("\"", "\\\"")
        )

        result, error = subprocess(command=command, out_error=True)

        self._error_action(error=error)
        reverse_result = self._reverse_flags(error=error)
        if reverse_result is not False:
            return reverse_result

        return result

    def _get_script_params(self) -> (None, dict):
        bad_values = [None, '', 'None']
        params_dict = {'script': self.instance.script, 'bin': self.instance.script_bin, 'arg': self.instance.script_arg}

        if isinstance(self.instance, GaOutputDevice):
            if self.instance.reverse == 1 and self.instance.active:
                if self.reverse:
                    if self.instance.reverse_script is not None:
                        params_dict['script'] = self.instance.reverse_script

                    if self.instance.reverse_script_arg is not None:
                        params_dict['arg'] = self.instance.reverse_script_arg

                    if self.instance.reverse_script_bin is not None:
                        params_dict['bin'] = self.instance.reverse_script_bin

                else:
                    self.logger.write(f"Device \"{self.instance.name}\" is reverseable and active, but should not be reversed", level=4)
                    return None

        if params_dict['script'] in bad_values or params_dict['bin'] in bad_values:  # it should only be possible to be NoneType-None
            self.logger.write(f"No script or binary provided to execute for device \"{self.instance.name}\"", level=2)
            return None

        return params_dict

    def _error_action(self, error) -> None:
        if error not in [None, '']:
            self.logger.write(f"An error occurred while processing device \"{self.instance.name}\": \"{error}\"")
            self.instance.fail_count += 1

            if self.instance.fail_count > shared_vars.SYSTEM.device_fail_count:
                self.instance.fail_sleep = datetime.fromtimestamp(datetime.now().timestamp() + shared_vars.SYSTEM.device_fail_sleep)
                self.logger.write(f"Device \"{self.instance.name}\" has reached its fail threshold -> will skip execution "
                                  f"until \"{self.instance.fail_sleep.strftime('%Y-%m-%d %H:%M:%S:%f')}\"", level=3)

        else:
            self.instance.fail_count = 0

    def _reverse_flags(self, error) -> (bool, None):
        if isinstance(self.instance, GaOutputDevice):
            if error is None:
                if self.instance.reverse == 1:
                    if self.reverse:
                        self.instance.active = False
                        self.logger.write(f"Reverseable device \"{self.instance.name}\" was stopped", level=6)

                    else:
                        self.instance.active = True
                        self.logger.write(f"Reverseable device \"{self.instance.name}\" entered the active state", level=6)

                return True

            else:
                return None

        return False

    def _reverse_check(self):
        if isinstance(self.instance, GaOutputDevice) and self.instance.reverse == 1 and self.instance.active and not self.reverse:
            self.logger.write(f"Reverseable device \"{self.instance.name}\" is active and should not be reversed", level=5)
            return False

        elif isinstance(self.instance, GaConnectionDevice) and isinstance(self.nested_instance, GaOutputDevice) \
                and self.nested_instance.reverse == 1 and self.nested_instance.active and not self.reverse:
            self.logger.write(f"Reverseable device \"{self.nested_instance.name}\" is active and should not be reversed", level=5)
            return False

        return True
