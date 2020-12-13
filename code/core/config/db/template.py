# sql templates used throughout the core modules

from core.config.object.data.file import GaDataFile

file_config_dict = GaDataFile().get()

DB_NAME = file_config_dict['sql_database']

# templates

DEVICE_DICT = {
    'task': "INSERT INTO TaskLog (TaskResult, TaskMessage, TaskCategory, ObjectID) "
            "VALUES ('%s','%s','%s','%s');",
    'input': {
        'data': "INSERT INTO InputData (ObjectID, DataValue, DataValueID) VALUES ('%s','%s','%s');",
    },
    'output': {
        'data': {
            'time': "select DataValue, DataValueID from InputData where ObjectID = '%s' and created BETWEEN "
                    "TIMESTAMP('%s') and TIMESTAMP('%s') ORDER BY created DESC",
            'range': "select DataValue, DataValueID from InputData where ObjectID = '%s' ORDER BY created DESC LIMIT %s"
        }
    }
}

DB_CHECK_DICT = {
    'read': 'SELECT * FROM ga.test LIMIT 10;',
    'write': [
        'CREATE TABLE ga.test_%s;',
        'DROP TABLE ga.test_%s;'
    ]
}
