from sys import argv as sys_argv
from sys import path as sys_path

root_path = sys_argv[1]
action = sys_argv[2]
secret = sys_argv[3]

sys_path.append(root_path)

from core.utils.crypto import AESCipher
from core.utils.key import get as get_key


crypto = AESCipher(key=get_key())

if action == 'decrypt':
    print(crypto.decrypt(secret))

else:
    print(crypto.encrypt(secret))
