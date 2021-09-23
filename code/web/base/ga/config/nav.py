
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
            'Export': {
                'Config': '/system/export/config/',   # download db dump of config
                'Data': '/system/export/data/',  # download db dump of data
                'Full': '/system/export/full/',  # download db dump of all ga tables
            },
        },
    },
    'right': {
        '<i class="fab fa-youtube fa-2x ga-nav-right-icon" title="YouTube"></i>': 'https://www.youtube.com/channel/UCLJyDlo3Z6eP_X2Pw0-Z8Pw',
        '<i class="fab fa-github-square fa-2x ga-nav-right-icon" title="GitHub"></i>': 'https://github.com/superstes/growautomation',
        '<i class="fas fa-coins fa-2x ga-nav-right-icon" title="Donate"></i>': 'https://www.patreon.com/growautomation/membership',
        '<i class="fas fa-bug fa-2x ga-nav-right-icon" title="Report bug"></i>': 'https://github.com/superstes/growautomation/issues/new',
        '<i class="fas fa-book fa-2x ga-nav-right-icon" title="Documentation"></i>': 'https://docs.growautomation.eu',
        '<i class="fas fa-sign-out-alt fa-2x ga-nav-right-icon ga-nav-right-icon-logout" title="Logout"></i>': '/logout/',
    }
}
