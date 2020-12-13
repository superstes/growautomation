from ..models import SuperBareModel, models
from .objects import ObjectInputModel


class InputDataModel(SuperBareModel):
    field_list = ['data', 'obj']

    data = models.CharField(max_length=50)
    obj = models.ForeignKey(ObjectInputModel, on_delete=models.CASCADE, related_name='id_fk_obj')
    # todo: value-type mapping?

    def __str__(self):
        return f"Input data of device {self.obj.name}: {self.data}"


# todo: implement for all object tables
# class TaskLogModel(SuperBareModel):
#     field_list = ['category', 'result', 'message', 'obj']
#
#     category = models.CharField(max_length=50)
#     result = models.CharField(max_length=50)
#     message = models.CharField(max_length=255)
#     obj = models.ForeignKey('ObjectModel', on_delete=models.CASCADE, related_name='tl_fk_obj')
#
#     def __str__(self):
#         return f"Task log of device {self.obj.name}: {self.category}; {self.result}"
