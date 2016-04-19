# -*- coding: utf-8 -*-

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
]


# Application definition
MODULES = [
    'statistics',
    'raw_statistics',
    'report',
    'storage_forms'
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'simple_history',
    'kmclient',
] + MODULES


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'simple_history.middleware.HistoryRequestMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR,  'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
            ],
        },
    },
]

DATABASES = {
    'kmclient': {
        'ENGINE': '',
        'HOST': '',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
    },
}

# Test database configuration
TEST_DATABASES = {}

DATABASE_ROUTERS = [
    'kmclient.kmclient_router.Router',
    'routers.DefaultRouter',
]

WSGI_APPLICATION = 'wsgi.application'


# Logging settings

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d%b %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {},
}
for app in MODULES:
    # add logging handlers to all modules
    LOGGING['loggers'][app] = {
        'handlers': ['mail_admins', 'console'],
        'level': 'DEBUG',
        'propagate': True,
    }


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


# Celery

CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'pickle'

from celery.schedules import crontab
CELERYBEAT_SCHEDULE = {
    'sync_statistics': {
        'task': 'sync_statistics',
        'schedule': crontab(minute='0', hour='0'),
    },
}

BROKER_URL = ""


# Other settings

# Описывает типы отчетов, которые используются в системе. нужно следить за
# соответствием url-name с первым значением чойса

REPORT_TYPE_ACTIVE_DEALERS = 'kmclient_manage'
REPORT_TYPE_INACTIVE_DEALERS = 'inactive_dealers'

TYPE_REPORT_CHOICES = (
    (REPORT_TYPE_ACTIVE_DEALERS, u'Отчёт по активным дилерам'),
    (REPORT_TYPE_INACTIVE_DEALERS, u'Отчёт по неактивным дилерам'),
)

SERVER_EMAIL = 'kmclient_statistics@error'

AUTHORIZATION_ACTION_UUID = None

# ENCRYPTION
# ВАЖНО! Изменение этого ключа требуется продублировать
# в сереврной части кмклиента и в самом кмклиенте
XOR_KEY = 'gZCYS9b7qAe6sIs%[;~Iu^~]99[bnpGl'


from settings_local import *

if not AUTHORIZATION_ACTION_UUID:
    raise ImproperlyConfigured("AUTHORIZATION_ACTION_UUID don't configure")
if not BROKER_URL:
    raise ImproperlyConfigured("BROKER_URL don't configure")
if not LOCAL_DATABASES:
    raise ImproperlyConfigured("LOCAL_DATABASES don't configure")
if DEBUG and 'kmclient' not in LOCAL_DATABASES:
    raise ImproperlyConfigured(
        "LOCAL_DATABASES don't contain 'kmclient' db configuration. "
        "Client will be block in PRODUCTION DB!!!"
    )

DATABASES.update(LOCAL_DATABASES)


if DEBUG:
    INTERNAL_IPS = ('127.0.0.1', )
    DISABLE_PANELS = []

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TOOLBAR_CALLBACK': lambda x: True
    }

    # additional modules for development
    INSTALLED_APPS += (
        'debug_toolbar',
    )
