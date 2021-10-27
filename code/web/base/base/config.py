from socket import socket, AF_INET, SOCK_DGRAM

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'REPLACE-WITH-PRODUCTION-KEY'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# get ip of current host
s = socket(AF_INET, SOCK_DGRAM)
s.connect(('1.1.1.1', 80))
own_ip = s.getsockname()[0]
s.close()

ALLOWED_HOSTS = [own_ip, 'demo.growautomation.at', 'localhost']
TIME_ZONE = 'Europe/Vienna'
