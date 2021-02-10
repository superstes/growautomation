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
        return f"{self.name} | {self.description}"

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


# objects ##############################

from .submodels.objects import ObjectConnectionModel, ObjectInputModel, ObjectOutputModel, ObjectConditionLinkModel, ObjectConditionModel, ObjectControllerModel
from .submodels.objects import ObjectTimerModel

# data ##############################

from .submodels.data import InputDataModel, ChartGraphModel, ChartDatasetModel, ChartDashboardModel, ChartDatasetLinkModel, ChartGraphLinkModel
from .submodels.data import DashboardModel, DashboardPositionModel

# groups ##############################

from .submodels.groups import GroupConnectionModel, GroupInputModel, GroupOutputModel, GroupConditionModel, GroupAreaModel

# member ##############################

from .submodels.members import MemberConnectionModel, MemberInputModel, MemberOutputModel, MemberConditionLinkModel, MemberConditionModel
from .submodels.members import MemberConditionOutputGroupModel, MemberConditionOutputModel, MemberAreaModel, MemberConditionAreaGroupModel

# nested member ##############################

from .submodels.nestedmembers import NestedAreaModel

# settings ##############################

# from .submodels.settings import *

# test ##############################

from .submodels.test import *
