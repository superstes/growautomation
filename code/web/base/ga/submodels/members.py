from ..models import BaseMemberModel, models, BareModel

from .objects import ObjectConnectionModel, ObjectInputModel, ObjectOutputModel, ObjectConditionModel, ObjectConditionLinkModel
from .groups import GroupConnectionModel, GroupInputModel, GroupOutputModel, GroupConditionModel, GroupAreaModel


class MemberConnectionModel(BaseMemberModel):
    grp_model = GroupConnectionModel
    obj_model = ObjectConnectionModel
    initials = 'mc'

    group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name="%s_fk_group" % initials)
    obj = models.ForeignKey(obj_model, on_delete=models.CASCADE, related_name="%s_fk_obj" % initials)

    filter_dict = {'obj': {'obj': obj_model, 'pretty': 'Connection object'},
                   'group': {'obj': grp_model, 'pretty': 'Connection group'}}

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'obj'], name="mc_uc_group_obj")
        ]


class MemberInputModel(BaseMemberModel):
    grp_model = GroupInputModel
    obj_model = ObjectInputModel
    initials = 'mi'

    group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name="%s_fk_group" % initials)
    obj = models.ForeignKey(obj_model, on_delete=models.CASCADE, related_name="%s_fk_obj" % initials)

    filter_dict = {'obj': {'obj': obj_model, 'pretty': 'Connection object'},
                   'group': {'obj': grp_model, 'pretty': 'Connection group'}}

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'obj'], name='mi_uc_group_obj')
        ]


class MemberOutputModel(BaseMemberModel):
    grp_model = GroupOutputModel
    obj_model = ObjectOutputModel
    initials = 'mo'

    group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name="%s_fk_group" % initials)
    obj = models.ForeignKey(obj_model, on_delete=models.CASCADE, related_name="%s_fk_obj" % initials)

    filter_dict = {'obj': {'obj': obj_model, 'pretty': 'Connection object'},
                   'group': {'obj': grp_model, 'pretty': 'Connection group'}}

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'obj'], name='mo_uc_group_obj')
        ]


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
        member_count = 0
        member = None

        for option in self.optional_list:
            value = getattr(self, option)
            if value is not None:
                member = value
                member_count += 1

        if 1 < member_count > 1:
            return False
        else:
            return member

    # todo: form error should be shown if more than one optional_field is filled
    # def clean(self):
    #     cleaned_data = super().clean()
    #     if not cleaned_data.get('obj') and not cleaned_data.get('group'):
    #         raise ValidationError({'obj': "You can't leave both fields as null"})

    def save(self, *args, **kwargs):
        if self.member is False:
            raise ValueError("Must choose exactly one owner for the setting")

        super().save(*args, **kwargs)


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


class MemberAreaModel(BaseMemberModel):
    field_list = ['area', 'connection_obj', 'connection_group', 'input_obj', 'input_group', 'output_obj', 'output_group']
    initials = 'ma'
    optional_list = ['connection_obj', 'connection_group',
                     'input_obj', 'input_group',
                     'output_obj', 'output_group']

    area = models.ForeignKey(GroupAreaModel, on_delete=models.CASCADE, related_name="%s_fk_group" % initials)

    connection_obj = models.ForeignKey(ObjectConnectionModel, on_delete=models.CASCADE, related_name="%s_fk_connectionobj" % initials, null=True, default=None, blank=True)
    connection_group = models.ForeignKey(GroupConnectionModel, on_delete=models.CASCADE, related_name="%s_fk_connectiongroup" % initials, null=True, default=None, blank=True)
    input_obj = models.ForeignKey(ObjectInputModel, on_delete=models.CASCADE, related_name="%s_fk_inputobj" % initials, null=True, default=None, blank=True)
    input_group = models.ForeignKey(GroupInputModel, on_delete=models.CASCADE, related_name="%s_fk_inputgroup" % initials, null=True, default=None, blank=True)
    output_obj = models.ForeignKey(ObjectOutputModel, on_delete=models.CASCADE, related_name="%s_fk_outputobj" % initials, null=True, default=None, blank=True)
    output_group = models.ForeignKey(GroupOutputModel, on_delete=models.CASCADE, related_name="%s_fk_outputgroup" % initials, null=True, default=None, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['area', 'connection_obj'], name="ma_uc_area_connection_obj"),
            models.UniqueConstraint(fields=['area', 'connection_group'], name="ma_uc_area_connection_group"),
            models.UniqueConstraint(fields=['area', 'input_obj'], name="ma_uc_area_input_obj"),
            models.UniqueConstraint(fields=['area', 'input_group'], name="ma_uc_area_input_group"),
            models.UniqueConstraint(fields=['area', 'output_obj'], name="ma_uc_area_output_obj"),
            models.UniqueConstraint(fields=['area', 'output_group'], name="ma_uc_area_output_group"),
        ]

    def __str__(self):
        return f"Member {self.member.name} in area {self.area.name}"

    @property
    def member(self):
        member_count = 0
        member = None

        for option in self.optional_list:
            value = getattr(self, option)
            if value is not None:
                member = value
                member_count += 1

        if 1 < member_count > 1:
            return False
        else:
            return member

    # todo: form error should be shown if more than one optional_field is filled
    # def clean(self):
    #     cleaned_data = super().clean()
    #     if not cleaned_data.get('obj') and not cleaned_data.get('group'):
    #         raise ValidationError({'obj': "You can't leave both fields as null"})

    def save(self, *args, **kwargs):
        if self.member is False:
            raise ValueError("Must choose exactly one owner for the setting")

        super().save(*args, **kwargs)


class MemberConditionAreaGroupModel(BareModel):
    field_list = ['condition_group', 'group']

    condition_group = models.ForeignKey(GroupConditionModel, on_delete=models.CASCADE, related_name='cag_fk_condition_group')

    group = models.ForeignKey(GroupAreaModel, on_delete=models.CASCADE, related_name='cag_fk_group')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['condition_group', 'group'], name="cag_uc_condition_group"),
        ]
