from django.conf import settings
from django.utils.translation import gettext_lazy as _


API_TEACHER_URL = getattr(
    settings,
    'API_TEACHER_URL',
    (
        'https://storage.portale.unical.it/api/ricerca/'
        'teachers/'
    )
)

API_ADDRESSBOOK = getattr(
    settings,
    'API_ADDRESSBOOK',
    'https://storage.portale.unical.it/api/ricerca/addressbook/'
)

API_ADDRESSBOOK_FULL = getattr(
    settings,
    'API_ADDRESSBOOK_FULL',
    'https://storage.portale.unical.it/api/ricerca/addressbook-full/'
)

API_DECRYPTED_ID = getattr(
    settings,
    'API_DECRYPTED_ID',
    (
        'https://storage.portale.unical.it/api/ricerca/'
        'get-decrypted-person-id/'
    )
)

API_ENCRYPTED_ID = getattr(
    settings,
    'API_ENCRYPTED_ID',
    'https://storage.portale.unical.it/api/ricerca/get-person-id/'
)

OPERATOR_OFFICE = getattr(settings, 'OPERATOR_OFFICE',
                          'public-engagement-operator')

PATRONAGE_OFFICE = getattr(settings, 'PATRONAGE_OFFICE',
                           'public-engagement-patronage')

MANAGER_OFFICE = getattr(settings, 'MANAGER_OFFICE',
                         'public-engagement-manager')

EVALUATION_TIME_DELTA = getattr(settings, 'EVALUATION_TIME_DELTA', 0)

# STORAGE_TOKEN = ''
# token per comunicare con le API protette di storage.portale.unical.it

MANAGER_ALIAS_EMAILS = getattr(settings, 'MANAGER_ALIAS_EMAILS', [])

DOCUMENTATION_URL = getattr(
    settings,
    'DOCUMENTATION_URL',
    'https://unipublicengagement.readthedocs.io/it/latest/'
)

DASHBOARD_KPI_LIST = getattr(settings, 'DASHBOARD_KPI_LIST', [
    ('structure_counters', _('Number of events per structure')),
    ('events_recipients', _('Event type')),
    ('events_types', _('Recipients')),
    ('events_goals', _('Sustainable Development Goals (SDGs)')),
    ('events_methods_of_execution', _('Execution method')),
    ('events_geographical_dimension', _('Geographical dimension')),
    ('events_organizing_subjects', _('Main organizing entity of the initiative')),
    ('events_promo_channels', _('Promotion channels')),
    ('events_patronage_requested', _('Patronage request')),
    ('events_monitoring_data_provided', _('Monitoring activities')),
    ('events_impact_evaluation', _('Impact assessment plan')),
    ('events_scientific_areas', _('Scientific areas')),
])
