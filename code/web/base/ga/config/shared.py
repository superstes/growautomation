from django.conf import settings

# general settings
DATETIME_TS_FORMAT = '%Y-%m-%d %H:%M:%S'
CENSOR_SYMBOL = '●'
CENSOR_STRING = CENSOR_SYMBOL * 12
VERSION = 0.9
SQL_CONFIG_FILE = f'{settings.BASE_DIR}/database.cnf'
NONE_RESULTS = ['', 'None', None, ' ']

# privileges
LOGIN_URL = '/accounts/login/'
DENIED_URL = '/denied/'
DENIED_API_URL = '/api/denied/'
GA_USER_GROUP = 'ga_user'
GA_READ_GROUP = 'ga_read'
GA_WRITE_GROUP = 'ga_write'
GA_ADMIN_GROUP = 'ga_admin'

# log settings
LOG_MAX_TRACEBACK_LENGTH = 5000

# dashboard settings
DB_MAX_DATA_POINTS_SHORT_CLI = 75
DB_MAX_DATA_POINTS_MEDIUM_CLI = 250
DB_MAX_DATA_POINTS_LONG_CLI = 500
DB_MAX_DATA_POINTS_HUGE_CLI = 1500
DB_MAX_DATA_POINTS_SHORT_MOBILE = 35
DB_MAX_DATA_POINTS_MEDIUM_MOBILE = 100
DB_MAX_DATA_POINTS_LONG_MOBILE = 250
DB_MAX_DATA_POINTS_HUGE_MOBILE = 400

# other web ui settings
WEBUI_DEFAULT_REFRESH_SECS = 30
WEBUI_LOG_MAX_LOG_LINES = 25
WEBUI_MAX_ENTRY_RANGE = range(50, 3025, 50)
WEBUI_SVC_ACTION_COOLDOWN = 15
WEBUI_DEFAULT_DATA_TABLE_ROWS = 50
WEBUI_EMPTY_CHOICE = '---------'

# messages
WEBUI_WARNING_PUBLIC = 'You are accessing this web interface over a public network.<br><strong>This could be a security risk.<br></strong>' \
                       'This web interface has not been tested for security vulnerabilities.'
WEBUI_WARNING_UNENCRYPTED = '<strong>Your connection is unencrypted!</strong>'
WEBUI_WARNING_PUBLIC_UNENCRYPTED = '<strong>Your connection is unencrypted! And you are accessing this web interface over a public network.<br></strong>' \
                                   'You should consider setting up encryption via LetsEncrypt:<br><a href="https://docs.growautomation.eu">GrowAutomation documentation</a> ' \
                                   '| <a href="https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-20-04">Example tutorial</a>'