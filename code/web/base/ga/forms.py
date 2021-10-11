from django import forms
from django.core.exceptions import ValidationError

from .models import *
from .submodels.helper.matrix import Matrix
from .submodels.helper.crypto import encrypt
from .config.shared import CENSOR_SYMBOL
from .config.label import HELP_DICT, LABEL_DICT


# base ##############################

class BaseForm(forms.ModelForm):
    class Meta:
        abstract = True


class BaseMultiFKForm(BaseForm):
    def clean(self):
        super().clean()

        to_check = {}

        for field in self._meta.model.optional_list:
            label = LABEL_DICT[field] if field in LABEL_DICT else field
            to_check[label] = self.cleaned_data[field]

        fill_count = 0

        for value in to_check.values():
            if value is not None:
                fill_count += 1

        if fill_count != 1:
            raise ValidationError(f"You must fill exactly one of the following fields: \"{[label for label in to_check.keys()]}\"")


# devices ##############################

class ObjectConnectionForm(BaseForm):
    class Meta:
        model = ObjectConnectionModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class ObjectInputForm(BaseForm):
    class Meta:
        model = ObjectInputModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class ObjectOutputForm(BaseForm):
    class Meta:
        model = ObjectOutputModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class GroupConnectionForm(BaseForm):
    class Meta:
        model = GroupConnectionModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class GroupInputForm(BaseForm):
    class Meta:
        model = GroupInputModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class GroupOutputForm(BaseForm):
    class Meta:
        model = GroupOutputModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class MemberConnectionForm(BaseForm):
    class Meta:
        model = MemberConnectionModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class MemberInputForm(BaseForm):
    class Meta:
        model = MemberInputModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class MemberOutputForm(BaseForm):
    class Meta:
        model = MemberOutputModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


# area ##############################

class GroupAreaForm(BaseForm):
    class Meta:
        model = GroupAreaModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class MemberAreaForm(BaseMultiFKForm):
    class Meta:
        model = MemberAreaModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class NestedAreaForm(BaseForm):
    class Meta:
        model = NestedAreaModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


# condition ##############################

class ObjectConditionForm(BaseMultiFKForm):
    class Meta:
        model = ObjectConditionModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class ObjectSpecialConditionForm(BaseForm):
    class Meta:
        model = ObjectSpecialConditionModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class ObjectConditionLinkForm(BaseForm):
    class Meta:
        model = ObjectConditionLinkModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class GroupConditionForm(BaseForm):
    class Meta:
        model = GroupConditionModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class MemberConditionLinkForm(BaseMultiFKForm):
    class Meta:
        model = MemberConditionLinkModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class MemberConditionForm(BaseForm):
    class Meta:
        model = MemberConditionModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class MemberConditionOutputForm(BaseForm):
    class Meta:
        model = MemberConditionOutputModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class MemberConditionOutputGroupForm(BaseForm):
    class Meta:
        model = MemberConditionOutputGroupModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class MemberConditionAreaGroupForm(BaseForm):
    class Meta:
        model = MemberConditionAreaGroupModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


# system ##############################

class ObjectControllerForm(BaseForm):
    class Meta:
        model = ObjectControllerModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT

        widgets = {
            'sql_secret': forms.PasswordInput(render_value=True),
        }

    def clean(self):
        super().clean()

        submitted_plain_secret = self.cleaned_data['sql_secret']  # decrypt(instance.sql_secret)
        if self.instance is None:
            raise ValidationError('You must provide a valid sql password!')
        current_encrypted_secret = self.instance.sql_secret

        # if password was not changed -> set same one again
        if submitted_plain_secret.find(CENSOR_SYMBOL) != -1:
            self.cleaned_data['sql_secret'] = current_encrypted_secret

        # encrypt secret/password for storage in db if it was changed (else it is already encrypted)
        if submitted_plain_secret != current_encrypted_secret:
            self.cleaned_data['sql_secret'] = encrypt(submitted_plain_secret)


class ObjectTaskForm(BaseForm):
    class Meta:
        model = ObjectTaskModel
        fields = model.field_list
        labels = LABEL_DICT
        help_texts = HELP_DICT


class SystemScriptForm(forms.Form):
    script_name = forms.CharField(max_length=50)
    script_file = forms.FileField()


# data ##############################

class ChartGraphForm(BaseForm):
    class Meta:
        model = ChartGraphModel
        fields = model.field_list
        help_texts = HELP_DICT
        labels = LABEL_DICT


class ChartDashboardForm(BaseForm):
    class Meta:
        model = ChartDashboardModel
        fields = model.field_list
        help_texts = HELP_DICT
        labels = LABEL_DICT


class ChartDatasetForm(BaseForm):
    class Meta:
        model = ChartDatasetModel
        fields = model.field_list
        help_texts = HELP_DICT
        labels = LABEL_DICT
        widgets = {
            'start_ts': forms.HiddenInput(),
            'stop_ts': forms.HiddenInput(),
        }

    def clean(self):
        data = super().clean()
        input_device = data.get("input_device")
        input_model = data.get("input_model")
        start_ts = data.get("start_ts")
        period = data.get("period")
        period_data = data.get("period_data")

        if input_device and input_model:
            raise ValidationError("One one of the two can be chosen: 'input_device', 'input_model'")

        if start_ts and period:
            raise ValidationError("One one of the two can be chosen: 'start_ts', 'period'")

        if period and not period_data:
            raise ValidationError("Period data must be defined when period is chosen!")


class ChartGraphLinkForm(BaseForm):
    class Meta:
        model = ChartGraphLinkModel
        fields = model.field_list
        help_texts = HELP_DICT
        labels = LABEL_DICT
        widgets = {
            'group': forms.HiddenInput(),
        }


class ChartDatasetLinkForm(BaseForm):
    class Meta:
        model = ChartDatasetLinkModel
        fields = model.field_list
        help_texts = HELP_DICT
        labels = LABEL_DICT


class DashboardForm(BaseForm):
    class Meta:
        model = DashboardModel
        fields = model.field_list
        help_texts = HELP_DICT
        labels = LABEL_DICT

    def clean(self):
        data = super().clean()
        # todo: if rows/columns get changed -> need to validate that removed ones are empty


class DashboardPositionForm(BaseForm):
    class Meta:
        model = DashboardPositionModel
        fields = model.field_list
        help_texts = HELP_DICT
        labels = LABEL_DICT

    def clean(self):
        data = super().clean()
        matrix = data.get('dashboard').matrix
        xy_data = {'y0': data.get('y0'), 'y1': data.get('y1'), 'x0': data.get('x0'), 'x1': data.get('x1')}
        free, used_list = Matrix(matrix=matrix).check(xy_data=xy_data)

        if not free:
            if len(used_list) > 0:
                error = "Some fields in the dashboard matrix are already in use: \"%s\"" % used_list
            else:
                error = 'Placing of the element is not valid!'

            raise ValidationError(error, code='invalid')


class DashboardDefaultForm(BaseForm):
    class Meta:
        model = DashboardDefaultModel
        fields = model.field_list
        help_texts = HELP_DICT
        labels = LABEL_DICT
