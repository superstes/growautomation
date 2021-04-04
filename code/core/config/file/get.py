# pulls data from config file

from core.utils.crypto import AESCipher
from core.utils.key import get as get_key
from core.config import shared as shared_var

crypto = AESCipher(get_key())


def go(file: str, encrypted: bool):
    with open(file, 'r') as _:
        file_data_dict = {}

        for line in _.readlines():

            if encrypted:
                decrypted_line = crypto.decrypt(str.encode(line))

            else:
                decrypted_line = line

            try:
                key, value = decrypted_line.split('=')
                file_data_dict[key] = value.strip()

            except ValueError as error_msg:
                # log error or whatever
                pass

        return file_data_dict
