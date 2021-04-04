from ..models import BaseModel, models, BOOLEAN_CHOICES


# condition group

class GroupConditionModel(BaseModel):
    field_list = ['name', 'description', 'timer', 'enabled']

    enabled = models.BooleanField(choices=BOOLEAN_CHOICES, default=False)
    timer = models.SmallIntegerField(default=600)
