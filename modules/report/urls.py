# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

from report.views.inactive_dealers import InactiveDealersView
from report.views.kmclient_manage import (
    KmClientManagerView, GenerateFilterChoicesApi
)


urlpatterns = [
    url(r'^api/get_filter_choices/',
        csrf_exempt(GenerateFilterChoicesApi.as_view()),
        name='get_filter_choices'),
    url(r'^kmclient_manage/',
        staff_member_required(KmClientManagerView.as_view()),
        name='kmclient_manage'),
    url(r'^inactive_dealers/',
        staff_member_required(InactiveDealersView.as_view()),
        name=settings.REPORT_TYPE_INACTIVE_DEALERS),
]
