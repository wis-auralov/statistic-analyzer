# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.db import models

from picklefield import PickledObjectField


class StoredFormCollection(models.Model):
    """Позволяет хранить пользовательскую форму для формирования отчета
    В нее сериализуем с помощью pickle форму от пользователя и сохраняем в базу

    """
    name = models.CharField(u'Название', max_length=256, null=True,
                            blank=False)
    description = models.TextField(u'Описание', null=True, blank=True)
    report_type = models.CharField(u'Тип отчета', max_length=128,
                                   choices=settings.TYPE_REPORT_CHOICES,
                                   default=settings.TYPE_REPORT_CHOICES[0][0])
    pickled_form = PickledObjectField(u'Сериализованная форма')
    pickled_formset = PickledObjectField(u'Сериализованный формсет')

    def __unicode__(self):
        return self.name or u'Неизвестно'

    class Meta(object):
        verbose_name = u'Сохраненная форма'
        verbose_name_plural = u'Сохраненные формы'


