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
    description = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.name} | {self.description}"

    class Meta:
        abstract = True


class BaseDeviceModel(BaseModel):
    enabled = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)

    class Meta:
        abstract = True


class BaseDeviceObjectModel(BaseDeviceModel):
    connection = models.CharField(max_length=50)  # label Connection information [p.e. gpio pin]

    class Meta:
        abstract = True


class BaseDeviceGroupModel(BaseDeviceModel):
    script = models.CharField(max_length=50)  # label Script
    script_bin = models.CharField(max_length=100, default='/usr/bin/python3')  # label Script binary
    script_arg = models.CharField(max_length=255, blank=True, null=True, default=None)  # label Script argument

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

# data ##############################


from .submodels.data import InputDataModel


# groups ##############################

from .submodels.groups import GroupConnectionModel, GroupInputModel, GroupOutputModel, GroupConditionModel, GroupAreaModel


# member ##############################

from .submodels.members import MemberConnectionModel, MemberInputModel, MemberOutputModel, MemberConditionLinkModel, MemberConditionModel
from .submodels.members import MemberConditionOutputGroupModel, MemberConditionOutputModel, MemberAreaModel

# nested member ##############################

from .submodels.nestedmembers import NestedConnectionGroupModel, NestedInputGroupModel, NestedOutputGroupModel, NestedAreaModel


# settings ##############################

# from .submodels.settings import *
