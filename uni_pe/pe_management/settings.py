from django.conf import settings
from django.utils.translation import gettext_lazy as _


API_TEACHER_URL = getattr(
    settings,
    "API_TEACHER_URL",
    ("https://storage.portale.unical.it/api/ricerca/teachers/"),
)

API_ADDRESSBOOK = getattr(
    settings,
    "API_ADDRESSBOOK",
    "https://storage.portale.unical.it/api/ricerca/addressbook/",
)

API_ADDRESSBOOK_FULL = getattr(
    settings,
    "API_ADDRESSBOOK_FULL",
    "https://storage.portale.unical.it/api/ricerca/addressbook-full/",
)

API_DECRYPTED_ID = getattr(
    settings,
    "API_DECRYPTED_ID",
    ("https://storage.portale.unical.it/api/ricerca/get-decrypted-person-id/"),
)

API_ENCRYPTED_ID = getattr(
    settings,
    "API_ENCRYPTED_ID",
    "https://storage.portale.unical.it/api/ricerca/get-person-id/",
)

# operatori di struttura
STRUCTURE_OP_OFFICE = getattr(settings, "STRUCTURE_OP_OFFICE", "public-engagement-operator")
# operatori di struttura delegati alla verifica del patrocinio
STRUCTURE_PATRONAGE_OP_OFFICE = getattr(settings, "STRUCTURE_PATRONAGE_OP_OFFICE", "public-engagement-patronage")
# operatori di ateneo
MANAGER_OFFICE = getattr(settings, "MANAGER_OFFICE", "public-engagement-manager")
# membri degli organi di ateneo (CdA, Senato)
GOVERNING_BODIES_OFFICE = getattr(settings, "GOVERNING_BODIES_OFFICE", "public-engagement-government")
# delegati del Rettore
DELEGATES_OFFICE = getattr(settings, "DELEGATES_OFFICE", "public-engagement-delegates")

EVALUATION_TIME_DELTA = getattr(settings, "EVALUATION_TIME_DELTA", 0)

# STORAGE_TOKEN = ''
# token per comunicare con le API protette di storage.portale.unical.it

MANAGER_ALIAS_EMAILS = getattr(settings, "MANAGER_ALIAS_EMAILS", [])

DOCUMENTATION_URL = getattr(
    settings,
    "DOCUMENTATION_URL",
    "https://unipublicengagement.readthedocs.io/it/latest/",
)

DASHBOARD_GENERIC_KPI_LIST = getattr(
    settings,
    "DASHBOARD_GENERIC_KPI_LIST",
    [
        ("events_types", _("Event type")),
        ("events_goals", _("Sustainable Development Goals (SDGs)")),
        ("events_scientific_areas", _("Scientific areas")),
        ("events_geographical_dimension", _("Geographical dimension")),
        ("events_methods_of_execution", _("Execution method")),
        ("events_recipients", _("Recipients")),
        ("events_audience", _("Participating or reached audience")),
        ("events_organizing_subjects", _("Main organizing entity of the initiative")),
        ("events_involved_structures", _("Other UniCal involved structures")),
        ("events_collaborator_types", _("Collaborators types")),
        ("events_involved_personnel", _("Other UniCal involved personnel")),
        ("events_referents", _("Referents list")),

        
        # ~ ("events_promo_channels", _("Promotion channels")),
        # ~ ("events_patronage_requested", _("Patronage request")),
        # ~ ("events_monitoring_data_provided", _("Monitoring activities")),
        # ~ ("events_impact_evaluation", _("Impact assessment plan")),
    ],
)

DASHBOARD_MANAGER_KPI_LIST = getattr(
    settings,
    "DASHBOARD_MANAGER_KPI_LIST",
    [
        ("structure_counters", _("Number of events per structure")),
    ]
    + DASHBOARD_GENERIC_KPI_LIST,
)

DASHBOARD_OPERATOR_KPI_LIST = getattr(
    settings,
    "DASHBOARD_OPERATOR_KPI_LIST",
    DASHBOARD_GENERIC_KPI_LIST,
)
