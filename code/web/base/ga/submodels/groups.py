from pytz import common_timezones

from ..models import BaseDeviceGroupModel, BaseModel, models, BOOLEAN_CHOICES


# todo: area group with members

class GroupConnectionModel(BaseDeviceGroupModel):
    field_list = ['name', 'description', 'script', 'script_arg', 'script_bin', 'enabled']


class GroupInputModel(BaseDeviceGroupModel):
    field_list = ['name', 'description', 'script', 'script_arg', 'script_bin', 'unit', 'datatype', 'timer', 'enabled']
    DATATYPE_CHOICES = [
        ('bool', 'BOOLEAN (true or false)'),
        ('string', 'STRING (any characters)'),
        ('int', 'INTEGER (whole numbers)'),
        ('float', 'FLOAT (decimal numbers)'),
    ]

    unit = models.CharField(max_length=15, blank=True, null=True, default=None)  # label Input data unit
    timer = models.SmallIntegerField(default=600)
    datatype = models.CharField(max_length=50, choices=DATATYPE_CHOICES, default='int')  # label Input data value


class GroupOutputModel(BaseDeviceGroupModel):
    field_list = ['name', 'description', 'script', 'script_arg', 'script_bin', 'reverse', 'reverse_type', 'reverse_type_data',
                  'reverse_script', 'reverse_script_arg', 'reverse_script_bin', 'enabled']
    REVERSE_TYPE_CHOICES = [
        ('time', 'TIME (reverse the action after time in seconds)'),
        ('condition', "CONDITION (reverse the action after it's trigger has recovered)"),
    ]

    reverse = models.BooleanField(choices=BOOLEAN_CHOICES, default=True)
    reverse_type = models.CharField(max_length=20, choices=REVERSE_TYPE_CHOICES, blank=True, null=True, default=None)
    reverse_type_data = models.SmallIntegerField(blank=True, null=True, default=None)
    reverse_script = models.CharField(max_length=50, blank=True, null=True, default=None)  # label Script
    reverse_script_bin = models.CharField(max_length=100, blank=True, null=True, default=None)  # label Script binary
    reverse_script_arg = models.CharField(max_length=255, blank=True, null=True, default=None)  # label Script argument


class GroupConditionModel(BaseModel):
    field_list = ['name', 'description', 'timer', 'enabled']

    enabled = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)
    timer = models.SmallIntegerField(default=600)


class GroupAreaModel(BaseModel):
    field_list = ['name', 'description']
