# templates for database interaction used throughout the core modules

DEVICE_TMPL = {
    'task': "INSERT INTO ga_tasklog (created, result, message, category, obj_id) VALUES ('%s','%s','%s','%s','%s');",
    'input': {
        'data': "INSERT INTO ga_inputdatamodel (created, data, obj_id) VALUES ('%s','%s','%s');",
    },
    'output': {
        'data': {
            'time': "SELECT data FROM ga_inputdatamodel WHERE obj_id = '%s' AND created BETWEEN '%s' AND '%s' ORDER BY created DESC;",
            'range': "SELECT data FROM ga_inputdatamodel WHERE obj_id = '%s' ORDER BY created DESC LIMIT %s;"
        },
        'state': {
            'put': "INSERT INTO ga_devicestateoutput (created, updated, active, reverse_data, obj_id) VALUES ('%s','%s','%s','%s','%s');",
            'update': "UPDATE ga_devicestateoutput SET updated = '%s', active = '%s', reverse_data = '%s' WHERE obj_id = '%s';",
            'get': "SELECT active, reverse_data FROM ga_devicestateoutput WHERE obj_id = '%s';",
        },
        'log': "INSERT INTO ga_devicelogoutput (created, action, obj_id) VALUES ('%s','%s','%s');",
    },
}

TEST_TMPL = {
    'read': 'SELECT * FROM ga.ga_test LIMIT 10;',
    'write': [
        'CREATE TABLE ga.ga_test_%s (`stringi` varchar(10) NOT NULL, `booli` tinyint(1) NOT NULL);',
        'DROP TABLE ga.ga_test_%s;'
    ]
}
