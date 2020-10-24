# pulls data from config file

from core.utils.crypto import AESCipher
from core.utils.key import get as get_key

crypto = AESCipher(get_key())


def go(file):
    with open(file, 'r') as _:
        file_data_dict = {}

        for line in _.readlines():
            decrypted_line = crypto.decrypt(str.encode(line))
            key, value = decrypted_line.split('=')
            file_data_dict[key] = value

        return file_data_dict
