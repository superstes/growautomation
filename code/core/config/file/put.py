# writes config to file
# if setting already in file it should be replaced

from ...utils.crypto import AESCipher
from ...utils.key import get as get_key

crypto = AESCipher(get_key())


def go(file, data_dict: dict):
    with open(file, 'w') as _:
        replace_dict = {}
        file_data_dict = {}

        for line in _.readlines():
            decrypted_line = crypto.decrypt(line)
            key, value = decrypted_line.split('=')
            file_data_dict[key] = value

        for key, value in data_dict.items():
            if key in file_data_dict:
                if value != file_data_dict[key]:
                    replace_dict[key] = value
            else:
                replace_dict[key] = value

        write_dict = {**file_data_dict, **replace_dict}
        for key, value in write_dict.items():
            _.write(crypto.encrypt("%s=%s" % (key, value)))
