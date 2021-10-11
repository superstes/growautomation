# sql templates used throughout the core modules

from core.config import shared as config

DB_NAME = config.SYSTEM.sql_database

# templates

DEVICE_TMPL = {
    'task': "INSERT INTO ga_tasklog (created, result, message, category, obj_id) VALUES ('%s', '%s','%s','%s','%s');",
    'input': {
        'data': "INSERT INTO ga_inputdatamodel (created, data, obj_id) VALUES ('%s','%s','%s');",
    },
    'output': {
        'data': {
            'time': "select data from ga_inputdatamodel where obj_id = '%s' and created BETWEEN '%s' and '%s' ORDER BY created DESC",
            'range': "select data from ga_inputdatamodel where obj_id = '%s' ORDER BY created DESC LIMIT %s"
        }
    }
}

DB_CHECK_TMPL = {
    'read': 'SELECT * FROM ga.ga_test LIMIT 10;',
    'write': [
        'CREATE TABLE ga.ga_test_%s (`stringi` varchar(10) NOT NULL, `booli` tinyint(1) NOT NULL);',
        'DROP TABLE ga.ga_test_%s;'
    ]
}
