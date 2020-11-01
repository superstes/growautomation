# either
#   starts input script and pulls data for insertion into db
# or
#   starts output script


from core.utils.process import subprocess
from core.config import shared as shared_vars
from core.utils.debug import debugger
from core.device import lock

from json import dumps as json_dumps
from json import loads as json_loads


class Go:
    INPUT_CATEGORY = 'input'
    INPUT_DATA_KEY = 'data'
    OUTPUT_CATEGORY = 'output'
    SCRIPT_SUBPATH = "device/%s"

    def __init__(self, instance, category: str, reverse: bool = False):
        self.instance = instance
        self.category = category
        self.data = None
        self.reverse = reverse

    def start(self) -> (str, None):
        if lock.get(instance=self.instance):
            success = self._execute()

            lock.remove(instance=self.instance)
            debugger("device-process | start | instance '%s' output '%s' success '%s'"
                     % (self.instance.name, self.data, success))

            if self.category == self.INPUT_CATEGORY:
                try:
                    data = json_loads(self.data)
                    return data[self.INPUT_DATA_KEY]
                except KeyError:
                    return False
            else:
                return success

        else:
            debugger("device-process | _get_lock | instance '%s' gave up to get lock after '%s' sec"
                     % (self.instance.name, lock.LOCK_MAX_WAIT))
            return None

    def _execute(self):
        config_dict = {
            'connection': self.instance.connection,
        }

        function = self.instance.function
        function_arg = self.instance.function_arg
        function_bin = self.instance.function_bin

        if self.category == self.OUTPUT_CATEGORY:
            reverse = False
            if self.instance.reverse and self.instance.active and self.reverse:
                reverse = True
                function = self.instance.reverse_function
                function_arg = self.instance.reverse_function_arg
                function_bin = self.instance.reverse_function_bin

        command = "%s %s/%s/%s \"%s\" \"%s\"" % (
            function_bin,
            shared_vars.SYSTEM.path_root,
            self.SCRIPT_SUBPATH % self.category,
            function,
            function_arg,
            str(json_dumps(config_dict)).replace("\"", "\\\"")
        )

        result, error = subprocess(command=command, out_error=True)

        if error is not None:
            success = False
        else:
            success = True

        if self.category == self.INPUT_CATEGORY:
            self.data = result
        elif self.category == self.OUTPUT_CATEGORY and success:
            if reverse:
                self.instance.active = False
            elif self.instance.reverse and not self.instance.active:
                self.instance.active = True

        return success
