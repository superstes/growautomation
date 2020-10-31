# starts input script and pulls data for insertion into db

from core.utils.process import subprocess
from core.config import shared as shared_vars
from core.utils.debug import debugger
from core.device import lock

from json import dumps as json_dumps
from json import loads as json_loads


class Go:
    INPUT_SCRIPT_SUBPATH = 'device/input'
    INPUT_DATA_KEY = 'data'

    def __init__(self, instance):
        self.instance = instance
        self.data = None

    def start(self) -> (str, None):
        if lock.get(instance=self.instance):
            self._execute()
            lock.remove(instance=self.instance)
            debugger("input-process | start | instance '%s' output data '%s'" % (self.instance.name, self.data))
            return self.data[self.INPUT_DATA_KEY]
        else:
            debugger("input-process | _get_lock | instance '%s' gave up to get lock after '%s' sec"
                     % (self.instance.name, lock.LOCK_MAX_WAIT))
            return None

    def _execute(self):
        print("executing")
        config_dict = {
            'connection': self.instance.connection,
        }

        command = "%s %s/%s/%s %s %s" % (
            self.instance.function_bin,
            shared_vars.SYSTEM.path_root,
            self.INPUT_SCRIPT_SUBPATH,
            self.instance.function,
            self.instance.function_arg,
            json_dumps(config_dict)
        )

        json_data = subprocess(command=command)

        self.data = json_loads(json_data)
