from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from ..models import SuperBareModel, models, BaseModel, BOOLEAN_CHOICES, BaseMemberModel, BareModel
from .device import ObjectInputModel, GroupInputModel
from .area import GroupAreaModel
from .helper.matrix import Matrix

CHART_TYPE_CHOICES = [
    ('line', 'Line'), ('bar', 'Bar'), ('radar', 'Radar'), ('doughnut', 'Doughnut'), ('pie', 'Pie'), ('polarArea', 'polar Area'), ('bubble', 'Bubble'),
    ('scatter', 'Scatter'),
]


class InputDataModel(SuperBareModel):
    field_list = ['data', 'obj']

    data = models.CharField(max_length=50)
    obj = models.ForeignKey(ObjectInputModel, on_delete=models.CASCADE, related_name='id_fk_obj')
    # todo: value-type mapping?

    def __str__(self):
        return f"Input data of device {self.obj.name}: {self.data}"


class ChartGraphModel(BaseModel):
    field_list = [
        'name', 'description', 'chart_type', 'time_format_min', 'time_format_hour', 'time_format_day', 'time_format_month', 'chart_x_max_ticks', 'chart_y_max_suggest',
        'options_json', 'unit',
    ]

    chart_type = models.CharField(choices=CHART_TYPE_CHOICES, max_length=10)

    time_format_min = models.CharField(max_length=50, default='HH:mm')
    time_format_hour = models.CharField(max_length=50, default='HH:mm | DD-MM-YYYY')
    time_format_day = models.CharField(max_length=50, default='DD-MM-YYYY')
    time_format_month = models.CharField(max_length=50, default='MM-YYYY')

    chart_x_max_ticks = models.PositiveSmallIntegerField(default=15)
    chart_y_max_suggest = models.PositiveSmallIntegerField(blank=True, null=True, default=None)

    options_json = models.CharField(max_length=4096, blank=True, null=True, default=None)
    unit = models.CharField(max_length=15, blank=True, null=True, default=None)


class ChartDatasetModel(BaseModel):
    field_list = [
        'name', 'description', 'input_device', 'area', 'period', 'period_data',  'start_ts', 'stop_ts',  # 'input_model'  -> removed from form view
        'chart_fill', 'chart_fill_color', 'chart_border_color', 'chart_border_width', 'chart_type', 'chart_point_radius', 'chart_point_color', 'chart_point_type',
        'dataset_json',
    ]

    PERIOD_CHOICES = [('y', 'Years'), ('m', 'Months'), ('d', 'Days'), ('H', 'Hours'), ('M', 'Minutes')]
    CHART_POINT_TYPE_CHOICES = [
        ('circle', 'Circle'), ('cross', 'Cross'), ('crossRot', 'Cross rot'), ('dash', 'Dash'), ('line', 'Line'), ('rect', 'Rect'), ('rectRounded', 'Rect rounded'),
        ('rectRot', 'Rect rot'), ('star', 'Star'), ('triangle', 'Triangle')
    ]

    area = models.ForeignKey(GroupAreaModel, on_delete=models.CASCADE, related_name='cd_fk_area', blank=True, null=True, default=None)
    input_device = models.ForeignKey(ObjectInputModel, on_delete=models.CASCADE, related_name='cd_fk_input_device', blank=True, null=True, default=None)
    input_model = models.ForeignKey(GroupInputModel, on_delete=models.CASCADE, related_name='cd_fk_input_model', blank=True, null=True, default=None)

    # filter data
    start_ts = models.DateTimeField(blank=True, null=True, default=None)
    stop_ts = models.DateTimeField(blank=True, null=True, default=None)
    period = models.CharField(max_length=1, choices=PERIOD_CHOICES, blank=True, null=True, default=None)
    period_data = models.PositiveSmallIntegerField(blank=True, null=True, default=None)

    # chart options
    chart_type = models.CharField(choices=CHART_TYPE_CHOICES, max_length=10, blank=True, null=True, default=None)
    chart_fill = models.BooleanField(choices=BOOLEAN_CHOICES, blank=True, null=True, default=None)
    chart_fill_color = models.CharField(max_length=50, blank=True, null=True, default=None)
    chart_border_color = models.CharField(max_length=50, blank=True, null=True, default=None)
    chart_border_width = models.PositiveSmallIntegerField(blank=True, null=True, default=None)
    chart_point_radius = models.PositiveSmallIntegerField(blank=True, null=True, default=None)
    chart_point_color = models.CharField(max_length=50, blank=True, null=True, default=None)
    chart_point_type = models.CharField(choices=CHART_POINT_TYPE_CHOICES, max_length=15, blank=True, null=True, default=None)

    dataset_json = models.CharField(max_length=4096, blank=True, null=True, default=None)


class ChartDashboardModel(BaseModel):
    field_list = [
        'name', 'description',
    ]


class ChartGraphLinkModel(BaseMemberModel):
    grp_model = ChartDashboardModel
    obj_model = ChartGraphModel
    initials = 'cglm'

    group = models.OneToOneField(grp_model, on_delete=models.CASCADE, related_name=f"{initials}_fk_group")
    obj = models.ForeignKey(obj_model, on_delete=models.CASCADE, related_name=f"{initials}_fk_obj")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'obj'], name='cglm_uc_group_obj')
        ]


class ChartDatasetLinkModel(BaseMemberModel):
    grp_model = ChartDashboardModel
    obj_model = ChartDatasetModel
    initials = 'cdlm'

    group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name=f"{initials}_fk_group")
    obj = models.ForeignKey(obj_model, on_delete=models.CASCADE, related_name=f"{initials}_fk_obj")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'obj'], name='cdlm_uc_group_obj')
        ]


class DashboardModel(BaseModel):
    max_rows = 100
    max_columns = 30
    field_list = [
        'name', 'description', 'rows', 'columns',  # 'matrix' -> hidden in form
    ]

    rows = models.PositiveSmallIntegerField(default=4, validators=[MaxValueValidator(max_rows)])
    columns = models.PositiveSmallIntegerField(default=2, validators=[MaxValueValidator(max_columns)])
    matrix = models.TextField(
        max_length=Matrix.MAX_JSON_LEN,
        default=Matrix(y=max_rows, x=max_columns).get()
    )


class DashboardPositionModel(BareModel):
    field_list = [
        'y0', 'y1', 'x0', 'x1', 'dashboard', 'element',
    ]
    initials = 'dpm'
    # obj = models.ForeignKey(obj_model, on_delete=models.CASCADE, related_name="%s_fk_obj" % initials)
    dashboard = models.ForeignKey(DashboardModel, on_delete=models.CASCADE, related_name=f"{initials}_fk_dashboard")
    element = models.ForeignKey(ChartDashboardModel, on_delete=models.CASCADE, related_name=f"{initials}_fk_element")
    y0 = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(DashboardModel.max_rows - 1)])
    y1 = models.PositiveSmallIntegerField(default=2, validators=[MaxValueValidator(DashboardModel.max_rows)])
    x0 = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(DashboardModel.max_columns - 1)])
    x1 = models.PositiveSmallIntegerField(default=2, validators=[MaxValueValidator(DashboardModel.max_columns)])


@receiver(post_delete, sender=DashboardPositionModel)
def dpm_post_delete(sender, instance, **kwargs):
    xy_data = {'y0': instance.y0, 'y1': instance.y1, 'x0': instance.x0, 'x1': instance.x1}
    m = Matrix(matrix=instance.dashboard.matrix)

    if m.set(xy_data=xy_data, set_value=0):
        instance.dashboard.matrix = m.get()
        instance.dashboard.save()

    else:
        pass
        # log error or whatever ('Unable to update the dashboard matrix')


@receiver(post_save, sender=DashboardPositionModel)
def dpm_post_save(sender, instance, **kwargs):
    xy_data = {'y0': instance.y0, 'y1': instance.y1, 'x0': instance.x0, 'x1': instance.x1}
    m = Matrix(matrix=instance.dashboard.matrix)

    if m.set(xy_data=xy_data, set_value=instance.id):
        instance.dashboard.matrix = m.get()
        instance.dashboard.save()

    else:
        pass
        # log error or whatever ('Unable to update the dashboard matrix')


class DashboardDefaultModel(BareModel):
    field_list = [
        'dashboard', 'user',
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="ddm_fk_user")
    dashboard = models.ForeignKey(DashboardModel, on_delete=models.CASCADE, related_name="ddm_fk_dashboard")
