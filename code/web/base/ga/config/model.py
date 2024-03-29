# hardcoded model parameter that somebody might like to change
#   after changing those settings a db migration must be executed

# system settings
SYS_DEFAULT_ROOT_PATH = '/var/lib/ga'
SYS_DEFAULT_WEB_ROOT_PATH = '/var/www/ga'
SYS_DEFAULT_WEB_STATIC_PATH = '/var/www/ga_static'
SYS_DEFAULT_WEB_DOCS_PATH = '/var/www/ga_docs'
SYS_DEFAULT_HOME_CORE_PATH = '/home/ga_core'
SYS_DEFAULT_HOME_WEB_PATH = '/home/ga_web'
SYS_DEFAULT_LOG_PATH = '/var/log/ga'
SYS_DEFAULT_BACKUP_PATH = '/mnt/backup/ga'
SYS_DEFAULT_SQL_USER = 'ga_admin'
SYS_DEFAULT_SQL_DB = 'ga'
SYS_DEFAULT_TZ = 'UTC'
SYS_DEFAULT_FAIL_COUNT = 3
SYS_DEFAULT_FAIL_SLEEP = 3600
SYS_DEFAULT_SQL_SOCKET = '/run/mysqld/mysqld.sock'
SYS_DEFAULT_SQL_SVC = 'mariadb.service'
SYS_DEFAULT_SQL_CONFIG = '/etc/mysql/mariadb.conf.d/50-server.cnf'

# dashboard parameters
DB_MAX_ROWS = 100
DB_MAX_COLS = 30
DB_MATRIX_MAX_JSON_LEN = 30000
