# writes config to file
# if setting already in file it should be replaced

from core.utils.crypto import AESCipher
from core.utils.key import get as get_key
from core.config import shared as shared_var

crypto = AESCipher(get_key())


def go(file: str, data_dict: dict, encrypted: bool):
    with open(file, 'r+') as _:
        replace_dict = {}
        file_data_dict = {}

        for line in _.readlines():
            if encrypted:
                decrypted_line = crypto.decrypt(line)
            else:
                decrypted_line = line

            try:
                key, value = decrypted_line.split('=')
                file_data_dict[key] = value.strip()
            except ValueError as error_msg:
                # log error or whatever
                pass

        for key, value in data_dict.items():
            if key in file_data_dict:
                if value != file_data_dict[key]:
                    replace_dict[key] = value
            else:
                replace_dict[key] = value

        write_dict = {**file_data_dict, **replace_dict}
        first_line = True
        for key, value in write_dict.items():
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
