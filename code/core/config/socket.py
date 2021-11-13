# the addressing of functionality should be done like this:
#   we'll use a domain-like addressing to parse the requests
#
#   per example:
#     path: ga.core.device.output.3
#     action: start
#
#  the socket connection will enable these internal api-calls to be called from any external program (p.e. directly from a shell) [for external source shuffle might need to be turned off]
#  the main reason to implement this is the django (web) to core communication
#    we need to be able to start device-actions via the core from the webUI
#

from core.config import shared as config

# general socket settings
SOCKET_PORT = 2048
SOCKET_PUBLIC = False  # if not => the socket server will only be reachable locally

# transmission settings
SOCKET_SERVER_NAME = 'InterconnectionServer'
SOCKET_BANNER_CORE = f'### GrowAutomation {SOCKET_SERVER_NAME} ###'
PACKAGE_START = '+GA+'
PACKAGE_STOP = '-GA-'
PACKAGE_PATH_SEPARATOR = '_GA_'
PACKAGE_SIZE = 1024
RECV_INTERVAL = 2
RECV_TIMEOUT = config.AGENT.subprocess_timeout + 2  # we will need to wait longer than any action-process could run so the result can be transmitted
NONE_RESULT = 'none'

SHUFFLE = config.SOCKET_SHUFFLE

# todo: will set shuffle to true even if security == 0 ?!?!
# if config.SERVER.security == 1:
#     SHUFFLE = True

SHUFFLE_DATA = '80e7540fe29c6b88314a8083acf7110c'.encode('utf-8')

# api paths
PATH_CORE = 'ga.core'
SUB_PATH_DEVICE = 'device'
PATH_DEVICE_TYPES = ['input', 'output', 'connection']
MATCH_DEVICE = f'{PATH_CORE}{SUB_PATH_DEVICE}.([0-9]{{1,10}}).(.*?)$'
PATH_WEB = 'ga.web'
SUB_PATHS = [SUB_PATH_DEVICE]
