import sys

from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from organizational_area.models import *
from template.models import *
from template.validators import validate_file_size

from . settings import OPERATOR_OFFICE, EVALUATION_TIME_DELTA
from . validators import validate_poster_extension


def _get_year_choices():
    current_year = datetime.now().year
    return [(year, year) for year in range(2020, current_year + 1)]


_year_choices = _get_year_choices()
if 'makemigrations' in sys.argv or 'migrate' in sys.argv:  # pragma: no cover
    _year_choices = [('', '')]


def _poster_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "public-engagement/events/{0}/{1}".format(instance.event.id,
                                                     filename)


class PublicEngagementAnnualMonitoring(ActivableModel, CreatedModifiedBy, TimeStampedModel):
    # serve per definire chiudere o aprire le attività di PE in un anno
    year = models.IntegerField(unique=True)

    class Meta:
        verbose_name = "Anno di monitoraggio"
        verbose_name_plural = "Anni di monitoraggio"

    def __str__(self):
        return str(self.year)

    @staticmethod
    def year_is_active(year):
        cls = PublicEngagementAnnualMonitoring
        return cls.objects.filter(year=year, is_active=True).exists()


class PublicEngagementEventType(ActivableModel, CreatedModifiedBy, TimeStampedModel):
    description = models.CharField(max_length=500)

    class Meta:
        verbose_name = "Tipologia iniziativa"
        verbose_name_plural = "Tipologie iniziative"

    def __str__(self):
        return self.description


class PublicEngagementEvent(ActivableModel, CreatedModifiedBy, TimeStampedModel):
    title = models.CharField(_("Event title"), default='', max_length=300)
    start = models.DateTimeField(_("Start"))
    end = models.DateTimeField(_("End"))
    # dati referente
    referent = models.ForeignKey(get_user_model(),
                                 on_delete=models.PROTECT,
                                 related_name='%(class)s_referent',
                                 verbose_name=_("Referent"))
    structure = models.ForeignKey(OrganizationalStructure,
                                  on_delete=models.PROTECT,
                                  limit_choices_to={
                                      "is_active": True
                                  },
                                  verbose_name=_("Structure")
                                  )
    # pronto per la validazione
    to_evaluate = models.BooleanField(
        "Richiesta di validazione", default=False)
    evaluation_request_date = models.DateTimeField(
        "Data richiesta di validazione", null=True, blank=True)
    evaluation_request_by = models.ForeignKey(get_user_model(
    ), on_delete=models.PROTECT, null=True, blank=True, related_name='evaluation_request_by', verbose_name="Validazione richiesta da", )
    # evaluation operator
    operator_taken_date = models.DateTimeField(
        "Data presa in carico operatore", null=True, blank=True)
    operator_taken_by = models.ForeignKey(get_user_model(
    ), on_delete=models.PROTECT, null=True, blank=True, verbose_name="Presa in carico da operatore", related_name='operator_taken_by')
    operator_evaluation_date = models.DateTimeField(
        "Data validazione operatore", null=True, blank=True)
    operator_evaluation_success = models.BooleanField(
        "Validazione operatore positiva", default=False)
    operator_evaluated_by = models.ForeignKey(get_user_model(
    ), on_delete=models.PROTECT, null=True, blank=True, related_name='operator_evaluated_by', verbose_name="Validazione eseguita da operatore",)
    operator_notes = models.TextField("Note validazione operatore", default='', blank=True)
    # patronage operator
    patronage_operator_taken_date = models.DateTimeField(
        "Data presa in carico operatore patrocinio", null=True, blank=True)
    patronage_operator_taken_by = models.ForeignKey(get_user_model(
    ), on_delete=models.PROTECT, null=True, blank=True, related_name='patronage_taken_by', verbose_name="Presa in carico da operatore patrocinio",)
    patronage_granted = models.BooleanField("Patrocinio concesso", default=False,)
    patronage_granted_date = models.DateTimeField("Data validazione richiesta patrocinio", null=True, blank=True,)
    patronage_granted_by = models.ForeignKey(get_user_model(
    ), on_delete=models.PROTECT, null=True, blank=True, related_name='patronage_granted_by', verbose_name="Validazione patrocinio eseguita da operatore",)
    patronage_granted_notes = models.TextField("Note concessione patrocinio", default='', blank=True,)
    # manager
    created_by_manager = models.BooleanField("Creato dal manager", default=False)
    edited_by_manager = models.BooleanField("Modificato dal manager", default=False)
    disabled_notes = models.TextField("Note disabilitazione", default='', blank=True,)

    class Meta:
        verbose_name = "Iniziativa di Public Engagement"
        verbose_name_plural = "Iniziative di Public Engagement"

    def __str__(self):
        return f'{self.title} - {self.structure}'

    def is_started(self):
        """
        ci dice se l'iniziativa è iniziata
        """
        return self.start <= timezone.now()

    def is_over(self):
        """
        ci dice se l'iniziativa è terminata
        """
        return self.end < timezone.now()

    def starts_in_time(self):
        return self.start >= timezone.now() + timezone.timedelta(days=EVALUATION_TIME_DELTA)

    def is_editable_by_user(self):
        """
        ci dice se i dati dell'evento (generici e fase 1) sono editabili dall'utente
        controllando solo l'attuale stato e l'anno di management del PE
        non effettua controlli sul ruolo dell'utente
        delegati ad altre funzioni
        """
        if not self.is_active:
            return False
        # False: se il monitoraggio è chiuso per l'anno dell'iniziativa
        if not self.check_year():
            return False
        # False: se è stata già mandata in validazione
        if self.to_evaluate:
            return False
        # False: se è stata creata dal manager
        if self.created_by_manager:
            return False
        return True

    def has_report_editable(self):
        """
        ci dice se i dati di reportistica dell'evento (fase 2) sono editabili dall'utente
        controllando solo l'attuale stato e l'anno di management del PE
        non effettua controlli sul ruolo dell'utente
        delegati ad altre funzioni
        """
        if not self.is_active:
            return False
        # False: se il monitoraggio per l'anno è stato disabilitato
        if not self.check_year():
            return False
        # False: se non ci sono i dati della fase 1
        if not getattr(self, 'data', None):
            return False
        # False: se non sono stati inserite le persone collegate
        # if not self.data.involved_personnel.exists():
            # return False
        # False: se è stato creato dal manager
        if self.created_by_manager:
            return False
        # False: se i dati di monitoraggio sono stati editati dal manager
        if hasattr(self, 'report') and self.report.edited_by_manager:
            return False
        # False: se è stato bocciato
        if self.has_been_rejected(): # or self.is_evaluated_negatively_by_manager():
            return False
        # True: se l'evento è terminato
        if self.is_over():
            return True
        return False

    def has_report_editable_by_manager(self):
        """
        ci dice se i dati di reportistica dell'evento (fase 2) sono editabili dal manager
        """
        # False: se il monitoraggio per l'anno è stato disabilitato
        # ~ if not self.check_year():
            # ~ return False
        # False: se non ci sono i dati della fase 1
        if not getattr(self, 'data', None):
            return False
        # False: se non sono stati inserite le persone collegate
        # if not self.data.involved_personnel.exists():
            # return False
        # True: se l'evento è terminato
        if not self.is_over():
            return False
        # True: se l'ha creata il manager stesso
        if self.created_by_manager:
            return True
        # False: se non è stato approvato
        if self.has_been_approved():
            return True
        return False

    def is_ready_for_request_evaluation(self):
        """
        ci dice se l'evento può essere inviato a validazione
        """
        if not self.is_active:
            return False
        # False: se è stata creata dal manager
        if self.created_by_manager:
            return False
        # False: se il monitoraggio per l'anno è stato disabilitato
        if not self.check_year():
            return False
        # False: se è stata già mandata in validazione
        if self.to_evaluate:
            return False
        # False: se non ci sono i dati della fase 1
        if not getattr(self, 'data', None):
            return False
        # False: se non sono stati inserite le persone collegate
        # if not self.data.involved_personnel.exists():
            # return False
        # se l'evento deve ancora iniziare
        # si tiene conto del numero di giorni minimo
        # (settings.EVALUATION_TIME_DELTA)
        # ~ if self.starts_in_time():
            # ~ return True
        # se l'iniziativa è terminata
        # sono obbligatori anche i dati di monitoraggio
        if self.is_over() and not getattr(self, 'report', None):
            return False
        return True

    def evaluation_request_can_be_reviewed(self):
        """
        """
        if not self.is_active:
            return False
        # False: se il monitoraggio per l'anno è stato disabilitato
        if not self.check_year():
            return False
        # False: se dev'essere ancora effettuata
        if not self.to_evaluate:
            return False
        # False: se è stato già preso in carico dagli operatori
        if self.operator_taken_date:
            return False
        return True

    def can_be_handled_for_evaluation(self):
        """
        """
        if not self.is_active:
            return False
        # False: se il monitoraggio è chiuso per l'anno dell'iniziativa
        if not self.check_year():
            return False
        # False: se è stata già mandata in validazione
        if not self.to_evaluate:
            return False
        # False: se è già stato preso in carico da un operatore
        if self.operator_taken_date:
            return False
        # se l'iniziativa è stata creata da un manager
        if self.created_by_manager:
            return False
        return True

    def is_editable_by_operator(self):
        """
        """
        if not self.is_active:
            return False
        # False: se il monitoraggio è chiuso per l'anno dell'iniziativa
        if not self.check_year():
            return False
        # False: se l'operatore non ha preso in carico
        if not self.operator_taken_date:
            return False
        # False: se è stato già validato dall'operatore
        if self.operator_evaluation_date:
            return False
        # False: se è stato preso in carico da un operatore di patrocinio
        if self.patronage_operator_taken_date:
            return False
        # False: se è stato creato dal manager
        if self.created_by_manager:
            return False
        # False: se è stato modificato dal manager
        if self.edited_by_manager:
            return False
        return True

    def is_ready_for_evaluation(self):
        """
        """
        if not self.is_active:
            return False
        # False: se il monitoraggio per l'anno è stato disabilitato
        if not self.check_year():
            return False
        # False: se non sono stati inseriti i dati dell'iniziativa
        if not hasattr(self, 'data'):
            return False
        # if not self.data.involved_personnel.exists():
            # return False
        # False: se è già stata valutata
        if self.operator_evaluation_date:
            return False
        # False: se non è stato preso in carico dagli operatori
        if not self.operator_taken_date:
            return False
        # False: se è stato preso in carico da operatore patrocinio
        if self.patronage_operator_taken_date:
            return False
        # False: se il manager l'ha presa in carico
        if self.created_by_manager:
            return False
        return True

    def evaluation_can_be_reviewed(self):
        """
        """
        if not self.is_active:
            return False
        # False: se il monitoraggio per l'anno è stato disabilitato
        if not self.check_year():
            return False
        # False: se non è stato validato da un operatore
        if not self.operator_evaluation_date:
            return False
        # False: se è stato preso in carico da un operatore di patrocinio
        if self.patronage_operator_taken_date:
            return False
        # False: se è stata creata dal manager
        if self.created_by_manager:
            return False
        # False: se è stata modificata dal manager
        if self.edited_by_manager:
            return False
        return True

    def check_year(self):
        return PublicEngagementAnnualMonitoring.year_is_active(self.start.year)

    def can_be_handled_for_patronage(self):
        """
        """
        if not self.is_active:
            return False
        # False: se il monitoraggio è chiuso per l'anno dell'iniziativa
        if not self.check_year():
            return False
        # False: se l'operatore lo ha bocciato (e validato per esclusione)
        if not self.operator_evaluation_success:
            return False
        # False: se l'iniziativa è stata creata da un manager
        if self.created_by_manager:
            return False
        # False: se non è stato richiesto il patrocinio
        if not hasattr(self, 'data'):
            return False
        if not self.data.patronage_requested:
            return False
        # False: se l'iniziativa è già iniziata
        if self.is_started():
            return False
        if self.patronage_operator_taken_date:
            return False
        return True

    def is_ready_for_patronage_check(self):
        """
        """
        if not self.is_active:
            return False
        # False: se il monitoraggio è chiuso per l'anno dell'iniziativa
        if not self.check_year():
            return False
        # False: se l'operatore di patrocinio non lo ha preso in carico
        if not self.patronage_operator_taken_date:
            return False
        # False: se l'operatore di patrocinio lo ha validato
        if self.patronage_granted_date:
            return False
        # False: è stato creato dal manager
        if self.created_by_manager:
            return False
        # False: se non è stato richiesto il patrocinio
        if not hasattr(self, 'data'):
            return False
        if not self.data.patronage_requested:
            return False
        # False: se l'iniziativa è terminata
        if self.is_started():
            return False
        return True

    def patronage_can_be_reviewed(self):
        """
        """
        if not self.is_active:
            return False
        # False: se il monitoraggio per l'anno è stato disabilitato
        if not self.check_year():
            return False
        # False: se l'operatore di patrocinio non lo ha preso in carico
        if not self.patronage_operator_taken_date:
            return False
        # False: se l'operatore di patrocinio non lo ha validato
        if not self.patronage_granted_date:
            return False
        # False: il manager l'ha preso in carico
        if self.created_by_manager:
            return False
        # if self.edited_by_manager:
            # return False
        # False: se non è stato richiesto il patrocinio
        if not hasattr(self, 'data'):
            return False
        if not self.data.patronage_requested:
            return False
        if self.is_started():
            return False
        if self.edited_by_manager:
            return False
        return True

    def is_editable_by_manager(self):
        """
        """
        # False: se il monitoraggio è chiuso per l'anno dell'iniziativa
        # ~ if not self.check_year():
            # ~ return False
        # True: se è creato dal manager, sempre editabile
        if self.created_by_manager:
            return True
        # False: se non è stato approvato dalla struttura
        if not self.operator_evaluation_success:
            return False
        # False: se il patrocinio è stato richiesto ed è stato concesso (dati immutabili)
        # ~ if self.data.patronage_requested and self.patronage_granted:
            # ~ return False
        # True: se l'evento è finito
        if self.is_over():
            return True
        # False: se il patrocinio è stato richiesto
        # l'operatore di patrocinio l'ha preso in carico ma non è stato ancora emesso un responso
        if self.data.patronage_requested and self.patronage_operator_taken_date and not self.patronage_granted_date:
            return False
        return True

    def is_manageable_by_manager(self):
        """
        """
        # False: se il monitoraggio è chiuso per l'anno dell'iniziativa
        # ~ if not self.check_year():
            # ~ return False
        # True: se è creato dal manager, sempre editabile
        if self.created_by_manager:
            return True
        # False: se non è stato approvato dalla struttura
        if not self.operator_evaluation_success:
            return False
        return True

    def has_been_rejected(self):
        return self.operator_evaluation_date and not self.operator_evaluation_success

    def has_patronage_denied(self):
        return self.patronage_granted_date and not self.patronage_granted

    def has_been_approved(self):
        return self.operator_evaluation_date and self.operator_evaluation_success

    def has_patronage_granted(self):
        return self.patronage_granted_date and self.patronage_granted

    def clear_promo_info(self):
        if hasattr(self, 'data'):
            self.data.promo_channel.clear()
            self.data.promo_tool.clear()
            self.data.patronage_requested = False
            self.data.save(update_fields=['patronage_requested'])


class PublicEngagementEventMethodOfExecution(ActivableModel, CreatedModifiedBy, TimeStampedModel):
    description = models.CharField(max_length=254)

    class Meta:
        verbose_name = "Modalità di svolgimento"

    def __str__(self):
        return self.description


class PublicEngagementEventTarget(ActivableModel, CreatedModifiedBy, TimeStampedModel):
    description = models.CharField(max_length=254)

    class Meta:
        verbose_name = "Obiettivo iniziative"
        verbose_name_plural = "Obiettivi iniziative"

    def __str__(self):
        return self.description


class PublicEngagementEventPromoChannel(ActivableModel, CreatedModifiedBy, TimeStampedModel):
    description = models.CharField(max_length=254)
    is_global = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Canale di promozione"
        verbose_name_plural = "Canali di promozione"

    def __str__(self):
        return self.description

    def get_contacts(self, structure=None):
        contacts = PublicEngagementEventPromoChannelContact.objects.filter(promo_channel=self,
                                                                    is_active=True)
        if not self.is_global and structure:
            contacts = contacts.filter(structure=structure)
        return contacts.values_list('email', flat=True)


class PublicEngagementEventPromoChannelContact(ActivableModel, CreatedModifiedBy, TimeStampedModel):
    promo_channel = models.ForeignKey(PublicEngagementEventPromoChannel,
                                      on_delete=models.CASCADE,
                                      verbose_name=_("Contact"))
    email = models.EmailField(max_length=254)
    structure = models.ForeignKey(OrganizationalStructure,
                                  blank=True,
                                  null=True,
                                  verbose_name=_("Structure"),
                                  on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.promo_channel} - {self.email}"


class PublicEngagementEventPromoTool(ActivableModel, CreatedModifiedBy, TimeStampedModel):
    description = models.CharField(max_length=254)

    class Meta:
        verbose_name = "Strumento di promozione"
        verbose_name_plural = "Strumenti di promozione"

    def __str__(self):
        return self.description


class PublicEngagementEventRecipient(ActivableModel, CreatedModifiedBy, TimeStampedModel):
    description = models.CharField(max_length=254)

    class Meta:
        verbose_name = "Destinatario dell'iniziativa"
        verbose_name_plural = "Destinatari delle iniziative"

    def __str__(self):
        return self.description


class PublicEngagementEventScientificArea(ActivableModel, CreatedModifiedBy, TimeStampedModel):
    description = models.CharField(max_length=254)

    class Meta:
        verbose_name = "Area scientifica"
        verbose_name_plural = "Aree scientifica"

    def __str__(self):
        return self.description


class PublicEngagementEventCollaboratorType(ActivableModel, CreatedModifiedBy, TimeStampedModel):
    description = models.CharField(max_length=254)

    class Meta:
        verbose_name = "Tipo di collaboratore"
        verbose_name_plural = "Tipi di collaboratore"

    def __str__(self):
        return self.description


class PublicEngagementEventData(CreatedModifiedBy, TimeStampedModel):
    event = models.OneToOneField(PublicEngagementEvent,
                                 on_delete=models.CASCADE,
                                 related_name='data')
    event_type = models.ForeignKey(PublicEngagementEventType,
                                   on_delete=models.CASCADE,
                                   limit_choices_to={"is_active": True},
                                   verbose_name=_("Event type"))
    description = models.TextField(_("Short description"),
                                   max_length=1500,
                                   help_text=_("This text will be used for any promotion on institutional channels. Max 1500 chars"))
    involved_personnel = models.ManyToManyField(get_user_model(),
                                                verbose_name=_("Other UNICAL staff members involved in organizing/executing the initiative"))
    involved_structure = models.ManyToManyField(OrganizationalStructure,
                                                limit_choices_to={
                                                    "is_active": True
                                                },
                                                verbose_name=_("Other UNICAL structures involved in organizing/executing the initiative"))
    project_name = models.ForeignKey(PublicEngagementEvent,
                                     on_delete=models.PROTECT,
                                     null=True, blank=True,
                                     verbose_name=_("If the event is linked to a larger project, indicate which one"))
    recipient = models.ManyToManyField(PublicEngagementEventRecipient,
                                       limit_choices_to={'is_active': True},
                                       verbose_name=_("Recipients"))
    other_recipients = models.CharField(
        _("Other recipients"), default='', blank=True, max_length=254)
    target = models.ManyToManyField(PublicEngagementEventTarget,
                                    limit_choices_to={'is_active': True},
                                    blank=True,
                                    verbose_name=_("Sustainable Development Goals (SDGs)"))
    method_of_execution = models.ForeignKey(PublicEngagementEventMethodOfExecution,
                                            on_delete=models.PROTECT,
                                            limit_choices_to={'is_active': True},
                                            verbose_name=_("Execution method"))
    geographical_dimension = models.CharField(
        _("Geographical dimension"),
        default='',
        choices=[
            ('Internazionale', _('International')),
            ('Nazionale', _('National')),
            ('Regionale', _('Regional')),
            ('Locale', _('Local')),
        ],
        max_length=14
    )
    organizing_subject = models.CharField(
        _("Main organizing entity of the initiative"),
        default='',
        choices=[
            ('UniCal', _('University of Calabria (University, Department, or other structure)')),
            ('Altra università', _('Another university')),
            ('Altro ente pubblico', _('Another public entity')),
            ('Ente privato', _('Private entity')),
        ],
        max_length=20
    )
    promo_channel = models.ManyToManyField(PublicEngagementEventPromoChannel,
                                           limit_choices_to={'is_active': True},
                                           blank=True,
                                           verbose_name=_("Request for the initiative to be promoted through the following institutional communication channels"))
    patronage_requested = models.BooleanField(
        _("Request for the patronage of the Department/Center for the initiative"), default=False)
    promo_tool = models.ManyToManyField(PublicEngagementEventPromoTool,
                                        limit_choices_to={'is_active': True},
                                        blank=True,
                                        verbose_name=_("Request to use the Department/Center’s name and/or logo in the following communication tools"))
    poster = models.FileField(_("Poster attached"),
                              upload_to=_poster_directory_path,
                              null=True, blank=True,
                              validators=[validate_poster_extension,
                                          validate_file_size])

    class Meta:
        verbose_name = _("Event data")
        verbose_name_plural = _("Event data records")

    def __str__(self):
        return f"{self.event} - data"


class PublicEngagementEventReport(CreatedModifiedBy, TimeStampedModel):
    event = models.OneToOneField(PublicEngagementEvent,
                                 on_delete=models.CASCADE,
                                 related_name='report')
    participants = models.IntegerField(
        _("Non-academic audience participating in the initiative or reached via web/social resources, or outreach publications"))
    budget = models.FloatField(_("Total budget (in Euro)"))
    monitoring_activity = models.BooleanField(
        _("Is the initiative accompanied by monitoring activities (e.g., collection of information on activities, attendance, satisfaction, etc.)?"), default=False)
    impact_evaluation = models.BooleanField(
        _("Is the initiative accompanied by an impact evaluation plan?"), default=False)
    # other_structure = models.ManyToManyField(OrganizationalStructure,
                                             # limit_choices_to={
                                                 # "is_internal": True,
                                                 # "is_public_engagement_enabled": True,
                                                 # "is_active": True
                                             # },
                                             # verbose_name=_("Which other UNICAL structures (Departments or Centers) collaborated on this initiative?"))
    scientific_area = models.ManyToManyField(PublicEngagementEventScientificArea,
                                             verbose_name=_("Scientific areas"))
    collaborator_type = models.ManyToManyField(PublicEngagementEventCollaboratorType,
                                               limit_choices_to={"is_active": True},
                                               verbose_name=_("Which collaborators were involved in organizing/managing the initiative?"),
                                               blank=True)
    website = models.URLField(
        _("Initiative’s website"), blank=True, null=True)
    notes = models.TextField(_("Notes"), default='', blank=True)
    edited_by_manager = models.BooleanField("Modificato dal manager", default=False)

    class Meta:
        verbose_name = _("Event monitoring")
        verbose_name_plural = _("Event monitoring records")

    def __str__(self):
        return f"{self.event} - monitoring data"
