import os
import pathlib
from pathlib import Path


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'secret_key'

DEBUG = True

DEFAULT_HOST = 'your.host'
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://fqdn', ]
INTERNAL_IPS = ['127.0.0.1']
ADMIN_PATH = 'admin'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Application definition

INSTALLED_APPS = [
    'accounts',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.sites',

    'rest_framework',
    'django_filters',

    'organizational_area',
    'pe_management',

    'template',
    'django_unical_bootstrap_italia',
    'bootstrap_italia_template',

    # SAML2 SP
    # ~ 'djangosaml2',
    # ~ 'saml2_sp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middlewares.AccountsChangeDataMiddleware',
]

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = "accounts.User"

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'it-it'
LANGUAGE = LANGUAGE_CODE.split('-')[0]
TIME_ZONE = 'Europe/Rome'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# GETTEXT LOCALIZATION
MIDDLEWARE.append('django.middleware.locale.LocaleMiddleware')
LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)
#
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
DATA_DIR = os.path.join(BASE_DIR, "data")

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(DATA_DIR, 'static')
if not os.path.exists(STATIC_ROOT):
    pathlib.Path(STATIC_ROOT).mkdir(parents=True, exist_ok=True)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(DATA_DIR, 'media')
if not os.path.exists(MEDIA_ROOT):
    pathlib.Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)


# REST FRAMEWORK

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',  # dev server
    # add deploy server
    # add front-end server
]

# custom date/datetime format
DEFAULT_DATE_FORMAT = '%d/%m/%Y'
DEFAULT_TIME_FORMAT = '%H:%M'
DEFAULT_DATETIME_FORMAT = f'{DEFAULT_DATE_FORMAT} {DEFAULT_TIME_FORMAT}'

# override globals
DATE_INPUT_FORMATS = ['%Y-%m-%d', DEFAULT_DATE_FORMAT]
DATETIME_INPUT_FORMATS = [DEFAULT_DATETIME_FORMAT,
                          f'%Y-%m-%d {DEFAULT_TIME_FORMAT}']

# Saml2
# DjangoSAML2 conf
if 'djangosaml2' in INSTALLED_APPS:
    from saml2_sp.settings import *

    # pySAML2 SP mandatory
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True

    SAML2_URL_PREFIX = 'saml2'
    LOGIN_URL = f'/{SAML2_URL_PREFIX}/login'
    LOGOUT_URL = f'/{SAML2_URL_PREFIX}/logout'

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'djangosaml2.backends.Saml2Backend',
    )

    MIDDLEWARE.append('djangosaml2.middleware.SamlSessionMiddleware')
    SAML_SESSION_COOKIE_NAME = 'saml_session'
else:
    LOCAL_URL_PREFIX = 'local'
    LOGIN_URL = f'/{LOCAL_URL_PREFIX}/login/'
    LOGOUT_URL = f'/{LOCAL_URL_PREFIX}/logout/'

LOGOUT_REDIRECT_URL = f'/'

# smtp
# Default to dummy email backend. Configure dev/production/local backend
# as per https://docs.djangoproject.com/en/stable/topics/email/#email-backends
# EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
EMAIL_SENDER = 'mail@mail'
DEFAULT_FROM_EMAIL = EMAIL_SENDER
SERVER_EMAIL = 'mail@mail'
EMAIL_HOST = 'smtp_host'
# EMAIL_HOST_USER = 'myemail@hotmail.com'
# EMAIL_HOST_PASSWORD = 'mypassword'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = '[prefix] '

# logging
ADMINS = [
    ('name', 'email'),
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'default': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'detailed': {
            'format': '[%(asctime)s] %(message)s [(%(levelname)s)] %(args)s %(name)s %(filename)s.%(funcName)s:%(lineno)s]'
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "msg": %(message)s, "level": "%(levelname)s",  "name": "%(name)s", "path": "%(filename)s.%(funcName)s:%(lineno)s", "@source":"django-audit"}'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'formatter': 'detailed',
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'pe_management': {
            'handlers': ['mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

# email notification on error 500
DEFAULT_FROM_EMAIL = 'your@email.org'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_HOST = 'your.server.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
