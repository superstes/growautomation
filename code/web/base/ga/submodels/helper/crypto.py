from core.utils.crypto import AESCipher
from core.utils.key import get as get_key


crypto = AESCipher(key=get_key())


def encrypt(unencrypted_secret: str) -> str:
    return crypto.encrypt(unencrypted_secret)
