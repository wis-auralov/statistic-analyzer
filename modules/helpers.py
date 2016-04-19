# -*- coding: utf-8 -*-
from django.http.response import JsonResponse
from django.views.generic import View

API_OK = 'OK'
API_ERROR = 'ERROR'


class BaseApiView(View):
    @staticmethod
    def get_response(status, data=None, message=''):
        res = {
            'status': status,
            'message': message,
            'data': data if data else {}
        }
        status_code = 400 if status == API_ERROR else 200
        return JsonResponse(res, status=status_code)
