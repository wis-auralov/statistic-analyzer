# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from raw_statistics.views import (
    PutRawStatisticsView, PutEncryptRawStatisticsView
)


urlpatterns = [
    url(r'^put_statistics/',
        csrf_exempt(PutEncryptRawStatisticsView.as_view())),

    url(r'^put_decrypt_statistics/',
        csrf_exempt(PutRawStatisticsView.as_view())),
]
