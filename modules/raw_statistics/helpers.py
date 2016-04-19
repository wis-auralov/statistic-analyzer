# -*- coding: utf-8 -*-

import base64

from django.conf import settings
from Crypto.Cipher import XOR


def get_real_ip(request):
    """ Получение реального IP пользователя """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def xor_decode_dict(dictionary):
    """ Декодирует словарь алгоритмом XOR """
    result = {}
    for key, val in dictionary.iteritems():
        key = XOR.new(settings.XOR_KEY).decrypt(base64.decodestring(key))
        val = XOR.new(settings.XOR_KEY).decrypt(base64.decodestring(val))
        result[key] = val

    return result


def xor_encode_dict(dictionary):
    """ Кодирует словарь алгоритмом XOR """
    result = {}
    for key, val in dictionary.iteritems():
        key = base64.encodestring(XOR.new(settings.XOR_KEY).encrypt(key))
        val = base64.encodestring(XOR.new(settings.XOR_KEY).encrypt(val))
        result[key] = val

    return result


