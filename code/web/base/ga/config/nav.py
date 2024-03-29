from .shared import LOGOUT_URL

NAVIGATION = {
    'left': {
        'Data': {
            'Dashboard': '/data/dashboard/',
            'Charts': '/data/chart/',
            'Table': '/data/table/',
        },
        'Config': {
            'Input': '/config/list/inputgroup/',
            'Output': '/config/list/outputgroup/',
            'Connection': '/config/list/connectiongroup/',
            'Condition': '/config/list/conditiongroup/',
            'Area': '/config/list/areagroup/',
        },
        'System': {
            'Settings': '/system/config/',
            # 'Tasks': '/config/list/timerobject/',  # not yet finished implementing
            'Service': '/system/service/',  # status and restart of service(s)
            'Logs': '/system/log/',  # read various log files
            'Scripts': '/system/script/',  # upload or delete scripts
            'Users': '/system/user/',  # add, modify or delete users
            'Update': '/system/update/',
            'Backup': {
                'Config': '/system/export/config/',   # download db dump of config
                'Data': '/system/export/data/',  # download db dump of data
                'Full': '/system/export/full/',  # download db dump of all ga tables
            },
        },
    },
    'right': {
        'YT': {
            'element': '<i class="fab fa-youtube fa-2x ga-nav-right-icon" title="YouTube"></i>',
            'url': 'https://www.youtube.com/channel/UCLJyDlo3Z6eP_X2Pw0-Z8Pw',
            'login': False,
        },
        'GH': {
            'element': '<i class="fab fa-github-square fa-2x ga-nav-right-icon" title="GitHub"></i>',
            'url': 'https://github.com/superstes/growautomation',
            'login': False,
        },
        'DON': {
            'element': '<i class="fas fa-coins fa-2x ga-nav-right-icon" title="Donate"></i>',
            'url': 'https://github.com/sponsors/superstes',
            'login': False,
        },
        'BUG': {
            'element': '<i class="fas fa-bug fa-2x ga-nav-right-icon" title="Report bug"></i>',
            'url': '/docs/basic/bugs.html',
            'login': False,
        },
        'DOC': {
            'element': '<i class="fas fa-book fa-2x ga-nav-right-icon" title="Documentation"></i>',
            'url': '/docs/',
            'login': False,
        },
        'LO': {
            'element': '<i class="fas fa-sign-out-alt fa-2x ga-nav-right-icon ga-nav-right-icon-logout" title="Logout"></i>',
            'url': LOGOUT_URL,
            'login': True,
        },
    }
}
