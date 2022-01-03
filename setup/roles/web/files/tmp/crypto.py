from sys import argv as sys_argv

action = sys_argv[1]
secret = sys_argv[2]

from core.utils.crypto import AESCipher
from core.utils.key import get as get_key


crypto = AESCipher(key=get_key())

if action == 'decrypt':
    print(crypto.decrypt(secret))

else:
    print(crypto.encrypt(secret))
