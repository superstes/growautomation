from ..models import SuperBareModel, models, BaseModel, BOOLEAN_CHOICES, BaseMemberModel
from .objects import ObjectInputModel
from .groups import GroupAreaModel, GroupInputModel

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
        'options_json',
    ]

    chart_type = models.CharField(choices=CHART_TYPE_CHOICES, max_length=10)

    time_format_min = models.CharField(max_length=50, default='HH:mm')
    time_format_hour = models.CharField(max_length=50, default='HH:mm | DD-MM-YYYY')
    time_format_day = models.CharField(max_length=50, default='DD-MM-YYYY')
    time_format_month = models.CharField(max_length=50, default='MM-YYYY')

    chart_x_max_ticks = models.PositiveSmallIntegerField(default=15)
    chart_y_max_suggest = models.PositiveSmallIntegerField(blank=True, null=True, default=None)

    options_json = models.CharField(max_length=4096, blank=True, null=True, default=None)


class ChartDatasetModel(BaseModel):
    field_list = [
        'name', 'description', 'input_device', 'area', 'period', 'period_data',  # 'start_ts', 'stop_ts', 'input_model'  -> removed from form view
        'chart_fill', 'chart_fill_color', 'chart_border_color', 'chart_border_width', 'chart_type', 'chart_point_radius', 'chart_point_color', 'chart_point_type',
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


class ChartLinkModel(BaseMemberModel):
    grp_model = ChartGraphModel
    obj_model = ChartDatasetModel
    initials = 'cl'

    group = models.ForeignKey(grp_model, on_delete=models.CASCADE, related_name="%s_fk_group" % initials)
    obj = models.ForeignKey(obj_model, on_delete=models.CASCADE, related_name="%s_fk_obj" % initials)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'obj'], name='cl_uc_group_obj')
        ]
