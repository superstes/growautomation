# remove current content of the config file
# write new data to it


from core.utils.crypto import AESCipher
from core.utils.key import get as get_key

crypto = AESCipher(get_key())


def go(file, data_dict: dict):
    with open(file, 'w') as _:
        for key, value in data_dict.items():
            _.write("%s\n" % crypto.encrypt("%s=%s" % (key, value)).decode("utf-8"))
