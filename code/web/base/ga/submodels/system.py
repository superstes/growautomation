from pytz import common_timezones
from django.core.validators import MaxValueValidator, MinValueValidator

from ..models import BaseModel, models, BOOLEAN_CHOICES
from ..config import model as config

LOG_LEVEL_CHOICES = [
    (0, '0 (No logging)'),
    (1, '1 (Important error logs)'),
    (2, '2 (All error logs)'),
    (3, '3 (Important warning logs)'),
    (4, '4 (Warning logs)'),
    (5, '5 (Unimportant warning logs)'),
    (6, '6 (Informative logs)'),
    (7, '7 (Somehow interesting info logs)'),
    (8, '8 (Completely unnecessary logs)'),
    (9, '9 (GIMMEE all you got!!)'),
]
TIMEZONE_CHOICES = [(tz, tz) for tz in common_timezones]


class SystemAgentModel(BaseModel):
    field_list = [
        'name', 'description', 'sql_server', 'sql_port', 'sql_user', 'sql_secret', 'sql_database', 'log_level', 'debug', 'device_fail_count', 'device_fail_sleep', 'device_log',
        'svc_interval_status', 'svc_interval_reload', 'subprocess_timeout', 'sql_socket', 'sql_service', 'sql_config',
    ]

    version = models.CharField(max_length=16)
    version_detail = models.CharField(max_length=64)

    path_root = models.CharField(max_length=255, default=config.SYS_DEFAULT_ROOT_PATH)
    path_home = models.CharField(max_length=255, default=config.SYS_DEFAULT_HOME_CORE_PATH)
    path_log = models.CharField(max_length=255, default=config.SYS_DEFAULT_LOG_PATH)

    sql_server = models.CharField(max_length=50, default='localhost')
    sql_port = models.PositiveSmallIntegerField(default=3306, validators=[MaxValueValidator(65535), MinValueValidator(1)])
    sql_user = models.CharField(max_length=50, default=config.SYS_DEFAULT_SQL_USER)
    sql_secret = models.CharField(max_length=255, default='o1Qhr6zm1INEZcKjBIVB')
    sql_database = models.CharField(max_length=50, default=config.SYS_DEFAULT_SQL_DB)
    sql_socket = models.CharField(max_length=255, default=config.SYS_DEFAULT_SQL_SOCKET)
    sql_service = models.CharField(max_length=50, default=config.SYS_DEFAULT_SQL_SVC)
    sql_config = models.CharField(max_length=255, default=config.SYS_DEFAULT_SQL_CONFIG)

    log_level = models.PositiveSmallIntegerField(default=2, choices=LOG_LEVEL_CHOICES)
    debug = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)

    device_fail_count = models.PositiveSmallIntegerField(default=config.SYS_DEFAULT_FAIL_COUNT)
    device_fail_sleep = models.PositiveSmallIntegerField(default=config.SYS_DEFAULT_FAIL_SLEEP)
    device_log = models.BooleanField(choices=BOOLEAN_CHOICES, default=True)

    svc_interval_status = models.PositiveSmallIntegerField(default=3600)
    svc_interval_reload = models.PositiveSmallIntegerField(default=21600)
    subprocess_timeout = models.PositiveSmallIntegerField(default=60)


class SystemServerModel(BaseModel):
    field_list = [
        'name', 'description', 'sql_server', 'sql_port', 'sql_user', 'sql_secret', 'sql_database', 'log_level', 'debug', 'security', 'timezone', 'web_cdn', 'web_warn', 'ga_cloud',
        'ga_cloud_ddns', 'sql_service', 'letsencrypt'
    ]

    version = models.CharField(max_length=16)
    version_detail = models.CharField(max_length=64)

    path_core = models.CharField(max_length=255, default=config.SYS_DEFAULT_ROOT_PATH)
    path_web = models.CharField(max_length=255, default=config.SYS_DEFAULT_WEB_ROOT_PATH)
    path_web_static = models.CharField(max_length=255, default=config.SYS_DEFAULT_WEB_STATIC_PATH)
    path_home_core = models.CharField(max_length=255, default=config.SYS_DEFAULT_HOME_CORE_PATH)
    path_home_web = models.CharField(max_length=255, default=config.SYS_DEFAULT_HOME_WEB_PATH)
    path_log = models.CharField(max_length=255, default=config.SYS_DEFAULT_LOG_PATH)

    sql_server = models.CharField(max_length=50, default='localhost')
    sql_port = models.PositiveSmallIntegerField(default=3306, validators=[MaxValueValidator(65535), MinValueValidator(1)])
    sql_user = models.CharField(max_length=50, default=config.SYS_DEFAULT_SQL_USER)
    sql_secret = models.CharField(max_length=255, default='o1Qhr6zm1INEZcKjBIVB')
    sql_database = models.CharField(max_length=50, default=config.SYS_DEFAULT_SQL_DB)
    sql_service = models.CharField(max_length=50, default=config.SYS_DEFAULT_SQL_SVC)

    log_level = models.PositiveSmallIntegerField(default=2, choices=LOG_LEVEL_CHOICES)
    debug = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)
    security = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default=config.SYS_DEFAULT_TZ)

    web_cdn = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)
    web_warn = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)

    ga_cloud = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)
    ga_cloud_uuid = models.UUIDField(unique=True, blank=True, null=True, default=None)
    ga_cloud_token = models.TextField(max_length=16384, blank=True, null=True, default=None)
    ga_cloud_ddns = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)

    letsencrypt = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)


class ObjectTaskModel(BaseModel):
    field_list = ['name', 'description', 'timer', 'enabled', 'target', 'interval']
    TARGET_CHOICES = [
        ('backup', 'Backup'),
    ]
    INTERVAL_CHOICES = [
        ('0****', 'Hourly'),
        ('00***', 'Daily'),
        ('00**1-5', 'Weekdays'),
        ('00**6-0', 'Weekends'),
        ('000**', 'Monthly'),
        ('0000*', 'Yearly'),
        ('00**1', 'Monday'),
        ('00**2', 'Tuesday'),
        ('00**3', 'Wednesday'),
        ('00**4', 'Thursday'),
        ('00**5', 'Friday'),
        ('00**6', 'Saturday'),
        ('00**0', 'Sunday'),
    ]

    enabled = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)
    timer = models.PositiveIntegerField(default=0)
    target = models.CharField(max_length=30, default='backup', choices=TARGET_CHOICES)
    interval = models.CharField(max_length=15, default='00***', choices=INTERVAL_CHOICES)


class SystemServerDynDnsModel(BaseModel):
    field_list = ['ddns_option', 'ddns_record']
    ddns_record = models.CharField(max_length=32)
    ddns_option = models.CharField(max_length=16, default='random', choices=[
        ('random', 'Random'),
        ('word', 'Word')
    ])

    server = models.ForeignKey(SystemServerModel, on_delete=models.CASCADE, related_name='ssddm_fk_cont')
