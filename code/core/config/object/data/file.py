# file config object
#   holds path to config file
#   methods use submodules stored in $ga_root_path/core/config/file

from core.config.file.put import go as Put
from core.config.file.get import go as Get
from core.config.file.reset import go as Reset
from core.config.file.validate import Go as Validate
from core.config.file.update import get as Update
from core.config import shared as shared_var

from pathlib import Path


class GaDataFile:
    DIR_SUBTRACT_COUNT = 4  # how many dirs are it to get from here down to the ga root path
    CONFIG_FILE_PATH = '/core/config/file/core.conf'

    def __init__(self):
        self.file = self._config_path()
        self.encryption = self._check_encryption()

    @staticmethod
    def _validate(data) -> dict:
        return data
        # todo: implement validation
        # return Validate(data).get()

    @classmethod
    def _config_path(cls) -> str:
        current_path = Path(__file__).parent.absolute()
        ga_root_path = '/'.join(str(current_path).split('/')[:-cls.DIR_SUBTRACT_COUNT])
        return "%s%s" % (ga_root_path, cls.CONFIG_FILE_PATH)

    def get(self) -> dict:
        data = Get(file=self.file, encrypted=self.encryption)
        return self._validate(data)

    def put(self, data: dict) -> None:
        validated_data = self._validate(data=data)
        return Put(file=self.file, data_dict=validated_data, encrypted=self.encryption)

    def update(self) -> None:
        update_data_dict = Update(current_config=self.get())
        self.encryption = shared_var.SYSTEM.security
        return self.reset(data=update_data_dict)

    def reset(self, data: dict):
        validated_data = self._validate(data=data)
        return Reset(file=self.file, data_dict=validated_data, encrypted=self.encryption)

    def _check_encryption(self) -> bool:
        try:
            return shared_var.SYSTEM.security

        except AttributeError:
            with open(self.file, 'r') as _:
                first_line = _.readline().strip()

                if first_line == shared_var.CRYPTO_RECOGNITION_TEXT:
                    # debug unencrypted
                    return False

                else:
                    # debug encrypted
                    return True
