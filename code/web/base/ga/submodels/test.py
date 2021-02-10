from ..models import models


class Test(models.Model):
    field_list = ['a', 'b']

    a = models.CharField(max_length=50)
    b = models.PositiveSmallIntegerField(default=15)
