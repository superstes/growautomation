# sql templates used throughout the core modules

from core.config.object.data.file import GaDataFile

file_config_dict = GaDataFile().get()

DB_NAME = file_config_dict['sql_database']

# templates

DEVICE_DICT = {
    'task': "INSERT INTO ga_tasklog (created, result, message, category, obj_id) VALUES ('%s', '%s','%s','%s','%s');",
    'input': {
        'data': "INSERT INTO ga_inputdatamodel (created, data, obj_id) VALUES ('%s','%s','%s');",
    },
    'output': {
        'data': {
            'time': "select data, obj_id from ga_inputdatamodel where obj_id = '%s' and created BETWEEN '%s' and '%s' ORDER BY created DESC",
            'range': "select data, obj_id from ga_inputdatamodel where obj_id = '%s' ORDER BY created DESC LIMIT %s"
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
