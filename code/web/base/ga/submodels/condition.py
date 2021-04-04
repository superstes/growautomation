from ..models import BaseModel, BareModel, models

from .condition_min import GroupConditionModel
from .device import ObjectInputModel, ObjectOutputModel, GroupInputModel, GroupOutputModel
from .area import GroupAreaModel


# condition match

class ObjectSpecialConditionModel(BaseModel):
    field_list = ['name', 'description']


class ObjectConditionModel(BaseModel):
    field_list = ['name', 'description', 'input_obj', 'input_group', 'special_obj', 'area', 'value', 'operator', 'check', 'period', 'period_data']
    optional_list = ['input_obj', 'input_group', 'special_obj']
    initials = 'co'
    OPERATOR_CHOICES = [
        ('=', 'EQUALS (data is the same as value)'),
        ('!=', 'NOT (data is not the same as value)'),
        ('<', '< (data is bigger than value)'),
        ('>', '> (data is smaller than value)'),
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

    input_obj = models.ForeignKey(ObjectInputModel, on_delete=models.CASCADE, related_name=f'{initials}_fk_input_obj', blank=True, null=True, default=None)
    input_group = models.ForeignKey(GroupInputModel, on_delete=models.CASCADE, related_name=f'{initials}_fk_input_group', blank=True, null=True, default=None)
    special_obj = models.ForeignKey(ObjectSpecialConditionModel, on_delete=models.CASCADE, related_name=f'{initials}_fk_special_obj', blank=True, null=True, default=None)
    area = models.ForeignKey(GroupAreaModel, on_delete=models.CASCADE, related_name=f'{initials}_fk_area', blank=True, null=True, default=None)
    value = models.CharField(max_length=50, default='value to compare')
    operator = models.CharField(max_length=3, choices=OPERATOR_CHOICES, default='=')
    check = models.CharField(max_length=3, choices=CHECK_CHOICES, default='avg')
    period = models.CharField(max_length=15, choices=PERIOD_CHOICES, default='time')
    period_data = models.SmallIntegerField(default=3600)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'input_obj', 'input_group', 'special_obj'], name="co_uc_name_input_obj_group_special"),
        ]


# condition link

class ObjectConditionLinkModel(BareModel):
    field_list = ['name', 'operator']
    OPERATOR_CHOICES = [
        ('and', 'AND (both correct)'),
        ('nand', 'NOT-AND (neither or one correct)'),
        ('or', 'OR (at least one correct)'),
        ('nor', 'NOT-OR (neither correct)'),
        ('xor', 'XOR (one of two correct)'),
        ('xnor', 'NOT-XOR (either none or both correct)'),
        ('not', 'NOT (first correct second incorrect)')
    ]

    name = models.CharField(max_length=50, unique=True)
    operator = models.CharField(max_length=5, choices=OPERATOR_CHOICES, default='and')

    def __str__(self):
        return f"{self.name} | Condition link"


# condition group


class MemberConditionAreaGroupModel(BareModel):
    field_list = ['condition_group', 'group']

    condition_group = models.ForeignKey(GroupConditionModel, on_delete=models.CASCADE, related_name='cag_fk_condition_group')
    group = models.ForeignKey(GroupAreaModel, on_delete=models.CASCADE, related_name='cag_fk_group')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['condition_group', 'group'], name="cag_uc_condition_group"),
        ]


class MemberConditionModel(BareModel):
    field_list = ['link', 'group']

    group = models.ForeignKey(GroupConditionModel, on_delete=models.CASCADE, related_name='cm_fk_group')
    link = models.ForeignKey(ObjectConditionLinkModel, on_delete=models.CASCADE, related_name='cm_fk_link')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'link'], name="cm_uc_group_link"),
        ]

    def __str__(self):
        return f"Member {self.link.name} of condition group {self.group.name}"


class MemberConditionOutputModel(BareModel):
    field_list = ['condition_group', 'obj']

    condition_group = models.ForeignKey(GroupConditionModel, on_delete=models.CASCADE, related_name='com_fk_condition_group')
    obj = models.ForeignKey(ObjectOutputModel, on_delete=models.CASCADE, related_name='com_fk_obj')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['condition_group', 'obj'], name="com_uc_condition_obj"),
        ]

    def __str__(self):
        return f"Member {self.obj.name} of condition group {self.condition_group.name}"


class MemberConditionOutputGroupModel(BareModel):
    field_list = ['condition_group', 'group']

    condition_group = models.ForeignKey(GroupConditionModel, on_delete=models.CASCADE, related_name='cog_fk_condition_group')
    group = models.ForeignKey(GroupOutputModel, on_delete=models.CASCADE, related_name='cog_fk_group')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['condition_group', 'group'], name="cog_uc_condition_group"),
        ]

    def __str__(self):
        return f"Member {self.group.name} of condition group {self.condition_group.name}"


# condition link #2

class MemberConditionLinkModel(BareModel):
    field_list = ['order', 'link', 'group', 'condition']
    optional_list = ['group', 'condition']
    ORDER_CHOICES = [
        (1, 'FIRST'),
        (2, 'SECOND'),
    ]

    order = models.SmallIntegerField(choices=ORDER_CHOICES)
    link = models.ForeignKey(ObjectConditionLinkModel, on_delete=models.CASCADE, related_name='clm_fk_link')

    group = models.ForeignKey(GroupConditionModel, on_delete=models.CASCADE, related_name='clm_fk_group', null=True, default=None, blank=True)
    condition = models.ForeignKey(ObjectConditionModel, on_delete=models.CASCADE, related_name='clm_fk_condition', null=True, default=None, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['link', 'group'], name="clm_uc_link_group"),
            models.UniqueConstraint(fields=['link', 'condition'], name="clm_uc_link_condition"),
            models.UniqueConstraint(fields=['link', 'order'], name="clm_uc_link_order"),
        ]

    def __str__(self):
        return f"Member {self.member.name} of condition link {self.link.name}"

    @property
    def member(self):
        for option in self.optional_list:
            value = getattr(self, option)
            if value is not None:
                return value
