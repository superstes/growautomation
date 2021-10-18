from ..models import BaseDeviceObjectModel, models, BaseDeviceModel, BOOLEAN_CHOICES, BaseMemberModel, BareModel, SuperBareModel

from .condition_min import GroupConditionModel


# connection

class ObjectConnectionModel(BaseDeviceObjectModel):
    field_list = ['name', 'description', 'connection', 'enabled']


class GroupConnectionModel(BaseDeviceModel):
    field_list = ['name', 'description', 'script', 'script_arg', 'script_bin', 'enabled']

    script = models.CharField(max_length=50)
    script_bin = models.CharField(max_length=100, default='python3')
    script_arg = models.CharField(max_length=255, blank=True, null=True, default=None)


class MemberConnectionModel(BaseMemberModel):
    grp_model = GroupConnectionModel
    obj_model = ObjectConnectionModel
    initials = 'mc'

    group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name=f"{initials}_fk_group")
    obj = models.ForeignKey(obj_model, on_delete=models.CASCADE, related_name=f"{initials}_fk_obj")

    filter_dict = {'obj': {'obj': obj_model, 'pretty': 'Connection object'},
                   'group': {'obj': grp_model, 'pretty': 'Connection group'}}

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'obj'], name="mc_uc_group_obj")
        ]


# input

class ObjectInputModel(BaseDeviceObjectModel):
    field_list = ['name', 'description', 'connection', 'downlink', 'timer', 'enabled']

    timer = models.SmallIntegerField(blank=True, null=True, default=None)
    downlink = models.ForeignKey(ObjectConnectionModel, on_delete=models.CASCADE, related_name='oi_fk_downlink', blank=True, null=True, default=None)


class GroupInputModel(BaseDeviceModel):
    field_list = ['name', 'description', 'script', 'script_arg', 'script_bin', 'unit', 'datatype', 'timer', 'enabled']
    DATATYPE_CHOICES = [
        ('bool', 'BOOLEAN (true or false)'),
        ('string', 'STRING (any characters)'),
        ('int', 'INTEGER (whole numbers)'),
        ('float', 'FLOAT (decimal numbers)'),
    ]

    script = models.CharField(max_length=50, blank=True, null=True, default=None)
    script_bin = models.CharField(max_length=100, blank=True, null=True, default='python3')
    script_arg = models.CharField(max_length=255, blank=True, null=True, default=None)
    unit = models.CharField(max_length=15, blank=True, null=True, default=None)
    timer = models.SmallIntegerField(default=600)
    datatype = models.CharField(max_length=50, choices=DATATYPE_CHOICES, default='int')


class MemberInputModel(BaseMemberModel):
    grp_model = GroupInputModel
    obj_model = ObjectInputModel
    initials = 'mi'

    group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name=f"{initials}_fk_group")
    obj = models.ForeignKey(obj_model, on_delete=models.CASCADE, related_name=f"{initials}_fk_obj")

    filter_dict = {'obj': {'obj': obj_model, 'pretty': 'Connection object'},
                   'group': {'obj': grp_model, 'pretty': 'Connection group'}}

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'obj'], name='mi_uc_group_obj')
        ]


# output

class ObjectOutputModel(BaseDeviceObjectModel):
    field_list = ['name', 'description', 'connection', 'downlink', 'enabled', 'reverse_condition']

    downlink = models.ForeignKey(ObjectConnectionModel, on_delete=models.CASCADE, related_name='oo_fk_downlink', blank=True, null=True, default=None)
    reverse_condition = models.ForeignKey(GroupConditionModel, on_delete=models.CASCADE, related_name='oo_fk_reverse_condition', blank=True, null=True, default=None)


class GroupOutputModel(BaseDeviceModel):
    field_list = ['name', 'description', 'script', 'script_arg', 'script_bin', 'reverse', 'reverse_type', 'reverse_type_data', 'reverse_condition',
                  'reverse_script', 'reverse_script_arg', 'reverse_script_bin', 'enabled']
    REVERSE_TYPE_CHOICES = [
        ('time', 'TIME (reverse the action after time in seconds)'),
        ('condition', "CONDITION (reverse the action after it's trigger has recovered)"),
    ]

    script = models.CharField(max_length=50, blank=True, null=True, default=None)
    script_bin = models.CharField(max_length=100, blank=True, null=True, default='python3')
    script_arg = models.CharField(max_length=255, blank=True, null=True, default=None)
    reverse = models.BooleanField(choices=BOOLEAN_CHOICES, default=True)
    reverse_type = models.CharField(max_length=20, choices=REVERSE_TYPE_CHOICES, blank=True, null=True, default=None)
    reverse_type_data = models.SmallIntegerField(blank=True, null=True, default=None)
    reverse_condition = models.ForeignKey(GroupConditionModel, on_delete=models.CASCADE, related_name='go_fk_reverse_condition', blank=True, null=True, default=None)
    reverse_script = models.CharField(max_length=50, blank=True, null=True, default=None)
    reverse_script_bin = models.CharField(max_length=100, blank=True, null=True, default=None)
    reverse_script_arg = models.CharField(max_length=255, blank=True, null=True, default=None)


class MemberOutputModel(BaseMemberModel):
    grp_model = GroupOutputModel
    obj_model = ObjectOutputModel
    initials = 'mo'

    group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name=f"{initials}_fk_group")
    obj = models.ForeignKey(obj_model, on_delete=models.CASCADE, related_name=f"{initials}_fk_obj")

    filter_dict = {'obj': {'obj': obj_model, 'pretty': 'Connection object'},
                   'group': {'obj': grp_model, 'pretty': 'Connection group'}}

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'obj'], name='mo_uc_group_obj')
        ]


class DeviceStateOutput(BareModel):
    initials = 'dso'
    obj = models.ForeignKey(ObjectOutputModel, on_delete=models.CASCADE, related_name=f"{initials}_fk_obj", unique=True)

    active = models.BooleanField(choices=BOOLEAN_CHOICES, default=True)
    reverse_data = models.CharField(max_length=32, blank=True, null=True, default=None)


class DeviceLogOutput(SuperBareModel):
    initials = 'dlo'
    obj = models.ForeignKey(ObjectOutputModel, on_delete=models.CASCADE, related_name=f"{initials}_fk_obj")
    action = models.CharField(max_length=32)
