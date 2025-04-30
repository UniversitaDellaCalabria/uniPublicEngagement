from django.conf import settings


API_TEACHER_URL = getattr(settings, 'API_TEACHER_URL',
                          'https://storage.portale.unical.it/api/ricerca/teachers/')
API_ADDRESSBOOK = getattr(settings, 'API_ADDRESSBOOK',
                          'https://storage.portale.unical.it/api/ricerca/addressbook/')
API_ADDRESSBOOK_FULL = getattr(settings, 'API_ADDRESSBOOK_FULL',
                               'https://storage.portale.unical.it/api/ricerca/addressbook-full/')
API_DECRYPTED_ID = getattr(settings, 'API_DECRYPTED_ID',
                           'https://storage.portale.unical.it/api/ricerca/get-decrypted-person-id/')
API_ENCRYPTED_ID = getattr(settings, 'API_ENCRYPTED_ID',
                           'https://storage.portale.unical.it/api/ricerca/get-person-id/')

OPERATOR_OFFICE = getattr(settings, 'OPERATOR_OFFICE',
                          'public-engagement-operator')
PATRONAGE_OFFICE = getattr(settings, 'PATRONAGE_OFFICE',
                           'public-engagement-patronage')
MANAGER_OFFICE = getattr(settings, 'MANAGER_OFFICE',
                         'public-engagement-manager')

EVALUATION_TIME_DELTA = getattr(settings, 'EVALUATION_TIME_DELTA', 0)

# STORAGE_TOKEN = ''  token per comunicare con le API protette di storage.portale.unical.it

MANAGER_ALIAS_EMAILS = getattr(settings, 'MANAGER_ALIAS_EMAILS', [])
