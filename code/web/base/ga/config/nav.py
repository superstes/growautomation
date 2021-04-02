
nav_dict = {
    'left': {
        'Data': {
            'Dashboard': '/data/dashboard/',
            'Table': '/data/table/',
            'Charts': '/data/chart/',
        },
        'Config': {
            'Connection': '/config/list/connectiongroup/',
            'Input': '/config/list/inputgroup/',
            'Output': '/config/list/outputgroup/',
            'Condition': '/config/list/conditiongroup/',
            'Area': '/config/list/areagroup/',
        },
        'System': {
            'Controller': '/config/list/controllerobject/',
            'Tasks': '/config/list/timerobject/',
            'Service': '/system/service/',  # status and restart of service(s)
            'Logs': '/system/log/',  # read various log files
            'Scripts': '/system/script/',  # upload or delete scripts
            'Export': '/system/export/',  # download db dump
        },
    },
    'right': {
        'Docs': 'https://docs.growautomation.eu',
        'GitHub': 'https://github.com/superstes/growautomation',
        'Submit bugs': 'https://docs.growautomation.eu/en/latest/basic/bugs.html',
        'Logout': '/logout/',
    }
}
