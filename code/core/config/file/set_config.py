from core.config.file.reset import go as reset
from core.config.file.get import go as get

file = '/etc/ga/core/config/file/core.conf'

reset(file, {'sql_server': '127.0.0.1', 'sql_port': '3306', 'sql_user': 'test', 'sql_secret': '789TMP01!', 'sql_database': 'ga'}, encrypted=False)

print(get(file, encrypted=False))
