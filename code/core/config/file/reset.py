# remove current content of the config file
# write new data to it

from core.utils.crypto import AESCipher
from core.utils.key import get as get_key
from core.config import shared as shared_var

crypto = AESCipher(get_key())


def go(file: str, data_dict: dict, encrypted: bool):
    with open(file, 'w') as _:
        first_line = True
        for key, value in data_dict.items():
            if encrypted:
                if first_line:
                    _.write("%s\n" % crypto.encrypt(shared_var.CRYPTO_RECOGNITION_TEXT).decode("utf-8"))
                    first_line = False
                _.write("%s\n" % crypto.encrypt("%s=%s" % (key, value)).decode("utf-8"))
            else:
                if first_line:
                    _.write("%s\n" % shared_var.CRYPTO_RECOGNITION_TEXT)
                    first_line = False
                _.write("%s=%s\n" % (key, value))
