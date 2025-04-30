from django.forms.widgets import *


class BootstrapItaliaDateTimeWidget(DateTimeInput):
    template_name = 'widgets/datetime.html'

    def __init__(self,  *attrs, **kwargs):
        super().__init__(*attrs, **kwargs)
        self.format = '%Y-%m-%d %H:%M'


class BootstrapItaliaToggleWidget(CheckboxInput):
    template_name = 'widgets/toggle.html'


class BootstrapItaliaMultiCheckboxWidget(CheckboxSelectMultiple):
    template_name = 'widgets/multicheckbox.html'
