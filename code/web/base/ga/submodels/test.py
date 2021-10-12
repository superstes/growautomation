from ..models import models


class Test(models.Model):
    # this table is used for db connectivity tests
    field_list = ['a', 'b']

    a = models.CharField(max_length=50)
    b = models.PositiveSmallIntegerField(default=15)
