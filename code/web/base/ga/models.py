from django.db import models


BOOLEAN_CHOICES = (
    (True, 'Yes'),
    (False, 'No')
)

# base ##############################


class SuperBareModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class BareModel(SuperBareModel):
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(BareModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True, default=None)

    def __str__(self):
        if self.description is not None:
            out = f'{self.name} | {self.description}'

        else:
            out = f'{self.name}'

        return out

    class Meta:
        abstract = True


class BaseDeviceModel(BaseModel):
    enabled = models.BooleanField(choices=BOOLEAN_CHOICES, default=True)

    class Meta:
        abstract = True


class BaseDeviceObjectModel(BaseDeviceModel):
    connection = models.CharField(max_length=50)  # label Connection information [p.e. gpio pin]

    class Meta:
        abstract = True


class BaseMemberModel(BareModel):
    field_list = ['group', 'obj']

    def __str__(self):
        return f"Group '{self.group.name}' with member '{self.obj.name}'"

    class Meta:
        abstract = True


class BaseNestedGroupModel(BareModel):
    field_list = ['group', 'nested_group']

    def __str__(self):
        return f"Group '{self.group.name}' with nested group '{self.nested_group.name}'"

    class Meta:
        abstract = True


# devices ##############################

from .submodels.device import ObjectInputModel, ObjectOutputModel, ObjectConnectionModel, GroupConnectionModel, GroupInputModel, GroupOutputModel
from .submodels.device import MemberConnectionModel, MemberInputModel, MemberOutputModel

# system ##############################

from .submodels.system import ObjectTaskModel, SystemAgentModel, SystemServerModel, SystemServerDynDnsModel

# condition ##############################

from .submodels.condition_min import GroupConditionModel
from .submodels.condition import ObjectConditionModel, ObjectConditionLinkModel, MemberConditionLinkModel, MemberConditionModel
from .submodels.condition import MemberConditionOutputGroupModel, MemberConditionOutputModel, MemberConditionAreaGroupModel, ObjectSpecialConditionModel

# data ##############################

from .submodels.data import InputDataModel, ChartGraphModel, ChartDatasetModel, ChartDashboardModel, ChartDatasetLinkModel, ChartGraphLinkModel
from .submodels.data import DashboardModel, DashboardPositionModel, DashboardDefaultModel

# area ##############################

from .submodels.area import MemberAreaModel, GroupAreaModel, NestedAreaModel

# test ##############################

from .submodels.test import Test
