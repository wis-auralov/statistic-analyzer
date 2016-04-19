# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib.postgres.fields import JSONField

from django.db import models


class RawClientActionLog(models.Model):
    """ Модель для хранения сырых логов событий от км-клиента
    """
    client_uuid = models.UUIDField(u'UUID клиента')
    action_uuid = models.UUIDField(u'UUID события')
    params = JSONField(u'Параметры')
    date = models.DateTimeField(u'Дата события', auto_now_add=True)
    processing_error = models.BooleanField(u'Ошибка обработки', default=False)

    class Meta:
        verbose_name = u'Сырые событие КМ-клиента'
        verbose_name_plural = u'Сырые события КМ-клиента'