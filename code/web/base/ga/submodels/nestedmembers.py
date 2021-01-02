from ..models import BaseNestedGroupModel, models

from .groups import GroupAreaModel


class NestedAreaModel(BaseNestedGroupModel):
    grp_model = GroupAreaModel
    initials = 'na'

    group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name="%s_fk_group" % initials)
    nested_group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name="%s_fk_nestedgroup" % initials)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'nested_group'], name='na_uc_group_nestedgroup')
        ]
