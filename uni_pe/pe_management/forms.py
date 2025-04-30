from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bootstrap_italia_template.widgets import *
from organizational_area.models import *

from template.widgets import *

from . models import *
from . settings import *
from . utils import user_is_manager
from . widgets import *


class PublicEngagementReferentForm(forms.Form):
    event_owner = forms.BooleanField(
        label=_("I'm the event referent"))


class PublicEngagementEventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        structure_slug = kwargs.pop('structure_slug', None)

        super().__init__(*args, **kwargs)

        if structure_slug:
            structures = OrganizationalStructure.objects.filter(
                slug=structure_slug)
            self.fields['structure'].queryset = structures

        if self.data:
            data = self.data.copy()
            data['start'] = f'{data["start_date"]} {data["start_time"]}'
            data['end'] = f'{data["end_date"]} {data["end_time"]}'
            self.data = data

    class Meta:
        model = PublicEngagementEvent
        fields = ['title', 'start', 'end', 'structure', ]
        widgets = {
            'start': BootstrapItaliaDateTimeWidget,
            'end': BootstrapItaliaDateTimeWidget,
        }

    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get('start')
        end = cleaned_data.get('end')

        if start and end and start > end:
            self.add_error(
                'start', _("The start date cannot be later than the end date"))
            self.add_error(
                'end', _("The start date cannot be later than the end date"))

        active_years = PublicEngagementAnnualMonitoring.objects.filter(
            is_active=True).values_list('year', flat=True)
        if start and start.year not in active_years:
            self.add_error(
                'start', _("It is not possible to enter dates for the year {}").format(start.year))

        if end and end > timezone.now() and self.instance.id and hasattr(self.instance, 'report'):
            self.add_error(
                'end', _("Since the monitoring data is already present, the initiative must have already ended"))


        if self.instance.id and hasattr(self.instance, 'data') and start <= timezone.now():
            if self.instance.data.patronage_requested or self.instance.data.promo_tool.exists() or self.instance.data.promo_channel.exists():
                self.add_error(
                    'start',
                    _("Data for the promotion of the initiative (promotion tools, promotion channels, etc...) and the request for patronage are not permitted if it has already started.")
                )

        return cleaned_data


class PublicEngagementEventOperatorForm(PublicEngagementEventForm):
    class Meta:
        model = PublicEngagementEvent
        fields = ['title', 'start', 'end', 'structure']
        widgets = {
            'start': BootstrapItaliaDateTimeWidget,
            'end': BootstrapItaliaDateTimeWidget,
        }


class PublicEngagementEventDataForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        by_user = kwargs.pop('by_user', False)
        event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        # se si stanno creando i dati per la prima volta
        # e l'evento è terminato o è già iniziato
        # non vengono riportati tutti i campi per la promozione
        # e il patrocinio
        if by_user and event.is_started():
            self.fields.pop('promo_channel', None)
            self.fields.pop('patronage_requested', None)
            # self.fields.pop('poster', None)
            self.fields.pop('promo_tool', None)
        if self.instance.id:
            # se l'operatore di patrocinio ha già preso in carico l'istanza
            # non facciamo più modificare i campi relativi al patrocinio
            if self.instance.event.patronage_operator_taken_date:
                self.fields.pop('patronage_requested', None)
                self.fields.pop('promo_tool', None)
            # se l'iniziativa è stata già approvata dalla struttura
            # non facciamo modificare la richiesta di promozione
            if self.instance.event.operator_evaluation_success:
                self.fields.pop('promo_channel', None)

    class Meta:
        model = PublicEngagementEventData
        fields = '__all__'
        exclude = ('id', 'created', 'created_by', 'modified',
                   'modified_by', 'event', 'involved_personnel', 'involved_structure')
        widgets = {
            'event_type': BootstrapItaliaRadioWidget(),
            'method_of_execution': BootstrapItaliaRadioWidget(),
            'geographical_dimension': BootstrapItaliaRadioWidget(),
            'organizing_subject': BootstrapItaliaRadioWidget(),
            'recipient': BootstrapItaliaMultiCheckboxWidget(),
            'target': BootstrapItaliaMultiCheckboxWidget(),
            'promo_channel': BootstrapItaliaMultiCheckboxWidget(),
            'promo_tool': BootstrapItaliaMultiCheckboxWidget(),
            'project_name': BootstrapItaliaAPISelectEventWidget(),
            'patronage_requested': BootstrapItaliaToggleWidget(),
            'description': forms.Textarea(attrs={'rows': 2})
        }

    class Media:
        js = ('js/textarea-autosize.js',)

    def clean(self):
        cleaned_data = super().clean()

        promo_channel = cleaned_data.get('promo_channel')
        patronage_requested = cleaned_data.get('patronage_requested')
        promo_tool = cleaned_data.get('promo_tool')
        poster = cleaned_data.get('poster')

        if patronage_requested and not promo_tool:
            self.add_error(
                'promo_tool', _("Make at least one choice if you require patronage"))
        if promo_channel and not poster:
            self.add_error(
                'poster', _("Mandatory field if you require the event to be promoted on institutional communication channels"))
        # se si stanno modificando dei dati
        if self.instance.id:
            # se il nome dell'evento scelto corrisponde a quello dell'evento stesso
            if self.instance.event == cleaned_data.get('project_name', None):
                self.add_error('project_name', _("It is not possible to connect to the same event"))
            # se la richiesta di patrocinio viene modificata ma
            # l'operatore di patrocinio aveva già preso in carico l'iniziativa
            # ~ if self.instance.event.patronage_operator_taken_date and not patronage_requested:
                # ~ self.add_error(
                    # ~ 'patronage_requested', _("It is not possible to cancel the patronage request if this has already been handled by a dedicated operator"))
            # ~ if self.instance.event.patronage_requested and not promo_tool:
                # ~ self.add_error(
                    # ~ 'promo_tool', _("Make at least one choice if you require patronage"))
            if self.instance.promo_channel and not poster:
                self.add_error(
                    'poster', _("Mandatory field if you require the event to be promoted on institutional communication channels"))
        return cleaned_data


class PublicEngagementEventReportForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
        # event = kwargs.pop('event')
        # super().__init__(*args, **kwargs)
        # self.fields['other_structure'].queryset = self.fields['other_structure'].queryset.exclude(
            # pk=event.structure.pk)

    class Meta:
        model = PublicEngagementEventReport
        fields = '__all__'
        exclude = ('id', 'created', 'created_by', 'modified',
                   'modified_by', 'event', 'edited_by_manager')
        widgets = {
            # 'other_structure': BootstrapItaliaMultiCheckboxWidget(),
            'scientific_area': BootstrapItaliaMultiCheckboxWidget(),
            'collaborator_type': BootstrapItaliaMultiCheckboxWidget(),
            'impact_evaluation': BootstrapItaliaToggleWidget(),
            'monitoring_activity': BootstrapItaliaToggleWidget(),
            'notes': forms.Textarea(attrs={'rows': 2})
        }
        help_texts = {
            'participants': 'Indicare una stima del numero di partecipanti',
            'budget': "Si intende il budget finanziario complessivo direttamente legato all'organizzazione/gestione dell'iniziativa. di Public Engagement. Qualora l'iniziativa è una sottoattività di un progetto più ampio non considerabile complessivamente come Public Engagement, è necessario scorporare e riportare solo il budget direttamente dedicato. Nel campo ‘euro’ possono essere inseriti solo numeri. Se l’iniziativa non ha previsto alcun budget finanziario, indicare 0 €",
            # 'other_structure': "Rispondere solo se l’ente organizzatore è “Università della Calabria"
        }

    class Media:
        js = ('js/textarea-autosize.js',)


class PublicEngagementEventEvaluationForm(forms.Form):
    success = forms.ChoiceField(
        label=_("Outcome"),
        choices=[
            (True, _("Positive")),
            (False,_("Negative"))
        ],
        widget=BootstrapItaliaRadioWidget)
    notes = forms.CharField(
        label='Note',
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        help_text=_("Mandatory in case of negative outcome"))

    def clean(self):
        cleaned_data = super().clean()

        success = cleaned_data.get('success')
        notes = cleaned_data.get('notes')
        if success == 'False' and not notes:
            self.add_error('notes', _("Mandatory in case of negative outcome"))

        return cleaned_data

    class Media:
        js = ('js/textarea-autosize.js',)


class PublicEngagementEventDisableEnableForm(forms.Form):
    notes = forms.CharField(
        label='Note',
        widget=forms.Textarea(attrs={'rows': 2}),
        required=True)

    class Media:
        js = ('js/textarea-autosize.js',)


class PublicEngagementStructureForm(forms.Form):
    structure = forms.IntegerField(label=_('Structure'),
                                    required=True,
                                    widget=BootstrapItaliaAPISelectStructureWidget())
