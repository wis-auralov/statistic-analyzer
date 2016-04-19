# -*- coding: utf-8 -*-

import json

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View

from raw_statistics.helpers import get_real_ip, xor_decode_dict
from raw_statistics.models import RawClientActionLog
from statistics.signals import client_login_action


class PutRawStatisticsView(View):
    @staticmethod
    def save_action_log(post, request):
        json_params = json.loads(post.get('params'))
        if post.get('action_uuid') == settings.AUTHORIZATION_ACTION_UUID:
            json_params['client_ip'] = get_real_ip(request)
            # декодируем, так как почему-то от kmclient приходит не юникод
            dealer_uname = post.get('dealer_uname', '').decode('cp1251')
            dealer_pass = post.get('dealer_pass', '').decode('cp1251')
            client_login_action.send(PutRawStatisticsView,
                                     client_uuid=post['client_uuid'],
                                     dealer_uname=dealer_uname,
                                     dealer_pass=dealer_pass,
                                     params=json_params)
        RawClientActionLog(
            client_uuid=post['client_uuid'],
            action_uuid=post['action_uuid'],
            params=json_params
        ).save()

    def post(self, request):
        self.save_action_log(request.POST, request)

        return HttpResponse()


class PutEncryptRawStatisticsView(PutRawStatisticsView):
    def post(self, request):
        post = xor_decode_dict(request.POST)
        self.save_action_log(post, request)

        return HttpResponse()