# hardcoded model parameter that somebody might like to change
#   after changing those settings a db migration must be executed

# controller
CONT_DEFAULT_ROOT_PATH = '/var/lib/ga'
CONT_DEFAULT_LOG_PATH = '/var/log/ga'
CONT_DEFAULT_BACKUP_PATH = '/mnt/backup/ga'
CONT_DEFAULT_SQL_USER = 'ga_admin'
CONT_DEFAULT_SQL_DB = 'ga'
CONT_DEFAULT_TZ = 'UTC'
CONT_DEFAULT_FAIL_COUNT = 3
CONT_DEFAULT_FAIL_SLEEP = 3600

# dashboard parameters
DB_MAX_ROWS = 100
DB_MAX_COLS = 30
DB_MATRIX_MAX_JSON_LEN = 30000
