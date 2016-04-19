# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, NoReverseMatch
from django.conf import settings

admin.autodiscover()

urlpatterns = [
    url(r'^', include(admin.site.urls)),
    url(r'^report/', include('report.urls')),
    url(r'^api/', include('raw_statistics.urls', namespace='raw_statistics')),
]

# проверка соответствия названий урлов с сеттингами
for report_choice in settings.TYPE_REPORT_CHOICES:
    try:
        reverse(report_choice[0])
    except NoReverseMatch as err:
        raise ImproperlyConfigured(
            'Error configuration of url-name[{0}]. Please check '
            'settings.TYPE_REPORT_CHOICES (first elem must be equal of'
            'url-name)'.format(report_choice[0])
        )