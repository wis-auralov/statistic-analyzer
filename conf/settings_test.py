# -*- coding: utf-8 -*-

from settings import *


if 'kmclient' not in TEST_DATABASES:
    raise ImproperlyConfigured(
        u"Необходимо настроить TEST_DATABASES['kmclient'] "
        u"на django.db.backends.postgresql_psycopg2 в settings_local"
    )
# переопределяем конфигурацию БД тестовой
DATABASES.update(TEST_DATABASES)


# Django требует миграции для создания своих приложений
# workaround disable migrations (for all apps)
# MIGRATION_MODULES = dict([
#     (m, m + '.migrations_not_used_in_tests') for m in INSTALLED_APPS
# ])

# По непонятной причине не работает для sqlite3 в памяти, а хотелось бы :(
# for key in DATABASES:
#     DATABASES[key]['ENGINE'] = 'django.db.backends.sqlite3'
#     DATABASES[key]['NAME'] = ':memory:'
#     if 'OPTIONS' in DATABASES[key]:
#         del DATABASES[key]['OPTIONS']