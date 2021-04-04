from ..models import BaseModel, BaseMemberModel, models, BaseNestedGroupModel

from .device import GroupConnectionModel, GroupOutputModel, GroupInputModel, ObjectInputModel, ObjectOutputModel, ObjectConnectionModel


# area

class GroupAreaModel(BaseModel):
    field_list = ['name', 'description']


class MemberAreaModel(BaseMemberModel):
    field_list = ['area', 'connection_obj', 'connection_group', 'input_obj', 'input_group', 'output_obj', 'output_group']
    initials = 'ma'
    optional_list = ['connection_obj', 'connection_group', 'input_obj', 'input_group', 'output_obj', 'output_group']

    area = models.ForeignKey(GroupAreaModel, on_delete=models.CASCADE, related_name=f"{initials}_fk_group")
    connection_obj = models.ForeignKey(ObjectConnectionModel, on_delete=models.CASCADE, related_name=f"{initials}_fk_connectionobj", null=True, default=None, blank=True)
    connection_group = models.ForeignKey(GroupConnectionModel, on_delete=models.CASCADE, related_name=f"{initials}_fk_connectiongroup", null=True, default=None, blank=True)
    input_obj = models.ForeignKey(ObjectInputModel, on_delete=models.CASCADE, related_name=f"{initials}_fk_inputobj", null=True, default=None, blank=True)
    input_group = models.ForeignKey(GroupInputModel, on_delete=models.CASCADE, related_name=f"{initials}_fk_inputgroup", null=True, default=None, blank=True)
    output_obj = models.ForeignKey(ObjectOutputModel, on_delete=models.CASCADE, related_name=f"{initials}_fk_outputobj", null=True, default=None, blank=True)
    output_group = models.ForeignKey(GroupOutputModel, on_delete=models.CASCADE, related_name=f"{initials}_fk_outputgroup", null=True, default=None, blank=True)

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
        for option in self.optional_list:
            value = getattr(self, option)
            if value is not None:
                return value


class NestedAreaModel(BaseNestedGroupModel):
    grp_model = GroupAreaModel
    initials = 'na'

    group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name=f"{initials}_fk_group")
    nested_group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name=f"{initials}_fk_nestedgroup")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'nested_group'], name='na_uc_group_nestedgroup')
        ]
