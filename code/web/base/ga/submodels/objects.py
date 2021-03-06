from pytz import common_timezones
from django.core.validators import MaxValueValidator, MinValueValidator

from ..models import BaseDeviceObjectModel, BaseModel, BareModel, models, BOOLEAN_CHOICES
from .groups import GroupInputModel


class ObjectConnectionModel(BaseDeviceObjectModel):
    field_list = ['name', 'description', 'connection', 'enabled']


class ObjectInputModel(BaseDeviceObjectModel):
    field_list = ['name', 'description', 'connection', 'downlink', 'timer', 'enabled']

    timer = models.SmallIntegerField(blank=True, null=True, default=None)
    downlink = models.ForeignKey(ObjectConnectionModel, on_delete=models.CASCADE, related_name='oi_fk_downlink', blank=True, null=True, default=None)


class ObjectOutputModel(BaseDeviceObjectModel):
    field_list = ['name', 'description', 'connection', 'downlink', 'enabled']

    downlink = models.ForeignKey(ObjectConnectionModel, on_delete=models.CASCADE, related_name='oo_fk_downlink', blank=True, null=True, default=None)


class ObjectConditionModel(BaseModel):
    field_list = ['name', 'description', 'input_obj', 'input_group', 'value', 'operator', 'check', 'period', 'period_data', 'special']
    optional_list = ['input_obj', 'input_group']
    OPERATOR_CHOICES = [
        ('=', '= (value is the same)'),
        ('!=', '!= (value is not the same)'),
        ('<', '< (value is bigger)'),
        ('>', '> (value is smaller)'),
    ]
    CHECK_CHOICES = [
        ('avg', 'AVG (average value of chosen datapool)'),
        ('min', 'MIN (smallest value in chosen datapool)'),
        ('max', 'MAX (biggest value in chosen datapool)'),
    ]
    PERIOD_CHOICES = [
        ('range', 'RANGE (count of datapoints)'),
        ('time', 'TIME (time range in seconds)'),
    ]

    input_obj = models.ForeignKey(ObjectInputModel, on_delete=models.CASCADE, related_name='co_fk_input_grp', blank=True, null=True, default=None)
    input_group = models.ForeignKey(GroupInputModel, on_delete=models.CASCADE, related_name='co_fk_input_group', blank=True, null=True, default=None)
    value = models.CharField(max_length=50, default='value to compare')
    operator = models.CharField(max_length=3, choices=OPERATOR_CHOICES, default='=')
    check = models.CharField(max_length=3, choices=CHECK_CHOICES, default='avg')
    period = models.CharField(max_length=15, choices=PERIOD_CHOICES, default='time')
    period_data = models.SmallIntegerField(default=3600)
    special = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'input_obj'], name="co_uc_name_input_obj"),
            models.UniqueConstraint(fields=['name', 'input_group'], name="co_uc_name_input_group"),
        ]

    @property
    def fks(self):
        fk_count = 0
        fk = None

        for option in self.optional_list:
            value = getattr(self, option)
            if value is not None:
                fk = value
                fk_count += 1

        if 1 < fk_count > 1:
            return False
        else:
            return fk

    def save(self, *args, **kwargs):
        if self.fks is False:
            raise ValueError("Must choose exactly one input object for the condition match")

        super().save(*args, **kwargs)


class ObjectConditionLinkModel(BareModel):
    field_list = ['name', 'operator']
    OPERATOR_CHOICES = [
        ('and', 'AND (both correct)'),
        ('nand', 'NOT-AND (neither or one correct)'),
        ('or', 'OR (at least one correct)'),
        ('nor', 'NOT-OR (neither correct)'),
        ('xor', 'XOR (either none or both correct)'),
        ('xnor', 'NOT-XOR (one of two correct)'),
        ('not', 'NOT (first correct second incorrect)')
    ]

    name = models.CharField(max_length=50, unique=True)
    operator = models.CharField(max_length=5, choices=OPERATOR_CHOICES, default='and')

    def __str__(self):
        return f"{ self.name } | Condition link"


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

    path_root = models.CharField(max_length=255, default='/etc/ga')
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


class ObjectTimerModel(BaseModel):
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
