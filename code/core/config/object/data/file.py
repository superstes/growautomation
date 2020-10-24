# file config object
#   holds path to config file
#   methods use submodules stored in $ga_root_path/core/config/file

from core.config.file.put import go as Put
from core.config.file.get import go as Get
from core.config.file.validate import Go as Validate
from core.config.file.update import Go as Update

from pathlib import Path


class GaDataFile:
    DIR_SUBTRACT_COUNT = 4  # how many dirs are it to get from here down to the ga root path
    CONFIG_FILE_PATH = '/core/config/file/core.conf'

    def __init__(self):
        self.file = self._config_path()

    @staticmethod
    def _validate(data) -> dict:
        return Validate(data).get()

    @classmethod
    def _config_path(cls) -> str:
        current_path = Path(__file__).parent.absolute()
        ga_root_path = '/'.join(str(current_path).split('/')[:-cls.DIR_SUBTRACT_COUNT])
        return "%s%s" % (ga_root_path, cls.CONFIG_FILE_PATH)

    def get(self) -> dict:
        data = Get(file=self.file)
        return self._validate(data)

    def put(self, data: dict) -> bool:
        validated_data = self._validate(data=data)
        return Put(file=self.file, data_dict=validated_data)

    def update(self) -> bool:
        update_data_dict = Update().get()
        return self.put(data=update_data_dict)
