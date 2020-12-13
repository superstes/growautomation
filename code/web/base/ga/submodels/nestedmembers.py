from ..models import BaseNestedGroupModel, models

from .groups import GroupConnectionModel, GroupInputModel, GroupOutputModel, GroupAreaModel


class NestedConnectionGroupModel(BaseNestedGroupModel):
    grp_model = GroupConnectionModel
    initials = 'ncg'

    group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name="%s_fk_group" % initials)
    nested_group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name="%s_fk_nestedgroup" % initials)

    filter_dict = {'nested_group': {'obj': grp_model, 'pretty': 'Nested group'},
                   'group': {'obj': grp_model, 'pretty': 'Connection group'}}

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'nested_group'], name='ncg_uc_group_nestedgroup')
        ]


class NestedInputGroupModel(BaseNestedGroupModel):
    grp_model = GroupInputModel
    initials = 'nig'

    group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name="%s_fk_group" % initials)
    nested_group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name="%s_fk_nestedgroup" % initials)

    filter_dict = {'nested_group': {'obj': grp_model, 'pretty': 'Nested group'},
                   'group': {'obj': grp_model, 'pretty': 'Connection group'}}

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'nested_group'], name='nig_uc_group_nestedgroup')
        ]


class NestedOutputGroupModel(BaseNestedGroupModel):
    grp_model = GroupOutputModel
    initials = 'nog'

    group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name="%s_fk_group" % initials)
    nested_group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name="%s_fk_nestedgroup" % initials)

    filter_dict = {'nested_group': {'obj': grp_model, 'pretty': 'Nested group'},
                   'group': {'obj': grp_model, 'pretty': 'Connection group'}}

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'nested_group'], name='nog_uc_group_nestedgroup')
        ]


class NestedAreaModel(BaseNestedGroupModel):
    grp_model = GroupAreaModel
    initials = 'na'

    group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name="%s_fk_group" % initials)
    nested_group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name="%s_fk_nestedgroup" % initials)

    filter_dict = {'nested_group': {'obj': grp_model, 'pretty': 'Nested group'},
                   'group': {'obj': grp_model, 'pretty': 'Connection group'}}

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'nested_group'], name='na_uc_group_nestedgroup')
        ]