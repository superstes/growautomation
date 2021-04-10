from pytz import common_timezones
from django.core.validators import MaxValueValidator, MinValueValidator

from ..models import BaseModel, models, BOOLEAN_CHOICES


class ObjectControllerModel(BaseModel):
    field_list = ['name', 'description', 'path_root', 'path_log', 'path_backup',
                  'sql_server', 'sql_port', 'sql_user', 'sql_secret', 'sql_database',
                  'log_level', 'debug', 'security', 'backup', 'timezone', 'web_cdn', 'web_warn',
                  'device_fail_count', 'device_fail_sleep', 'device_log']
    TIMEZONE_CHOICES = [(tz, tz) for tz in common_timezones]
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

    path_root = models.CharField(max_length=255, default='/var/lib/ga')
    path_log = models.CharField(max_length=255, default='/var/log/ga')
    path_backup = models.CharField(max_length=255, default='/mnt/backup/ga')

    sql_server = models.CharField(max_length=50, default='localhost')
    sql_port = models.PositiveSmallIntegerField(default=3306, validators=[MaxValueValidator(65535), MinValueValidator(1)])
    sql_user = models.CharField(max_length=50, default='ga_admin')
    sql_secret = models.CharField(max_length=255, default='o1Qhr6zm1INEZcKjBIVB')
    sql_database = models.CharField(max_length=50, default='ga')

    log_level = models.PositiveSmallIntegerField(default=2, choices=LOG_LEVEL_CHOICES)
    debug = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)
    security = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)
    backup = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default='UTC')

    device_fail_count = models.PositiveSmallIntegerField(default=3)
    device_fail_sleep = models.PositiveSmallIntegerField(default=3600)
    device_log = models.BooleanField(choices=BOOLEAN_CHOICES, default=True)

    web_cdn = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)
    web_warn = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)


class ObjectTaskModel(BaseModel):
    field_list = ['name', 'description', 'timer', 'enabled', 'target', 'interval']
    TARGET_CHOICES = [
        ('backup', 'Backup'),
    ]
    INTERVAL_CHOICES = [
        ('0****', 'Hourly'),
        ('00***', 'Daily'),
        ('00**1-5', 'Weekdays'),
        ('00**1-5', 'Weekends'),
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
    # could be changed to
    timer = models.PositiveIntegerField(default=0)
    target = models.CharField(max_length=30, default='backup', choices=TARGET_CHOICES)
    interval = models.CharField(max_length=15, default='00***', choices=INTERVAL_CHOICES)
