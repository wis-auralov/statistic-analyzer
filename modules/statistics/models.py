# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from uuid import uuid4

from django.db import models
from django.contrib.postgres.fields import JSONField
from simple_history.models import HistoricalRecords


class ActionGroup(models.Model):
    """ Группы событий км-клиента
    """
    name = models.CharField(u'Название', max_length=255)

    class Meta:
        verbose_name = u'Группа событий'
        verbose_name_plural = u'Группы событий'
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Action(models.Model):
    """ Типы событий км-клиента
    """
    uuid = models.UUIDField(u'UUID', unique=True, default=uuid4)
    name = models.CharField(u'Событие', max_length=255)
    action_group = models.ManyToManyField(
        ActionGroup, verbose_name=u'Группа событий', blank=True
    )

    class Meta:
        verbose_name = u'Событие'
        verbose_name_plural = u'События'
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Dealer(models.Model):
    """ Дополнительные свойства Дилера
    """
    uuid = models.UUIDField(u'UUID дилера', unique=True)
    name = models.CharField(u'Имя дилера', max_length=255, blank=True,
                            null=True)
    action_logging = models.ManyToManyField(Action, blank=True)
    action_group_logging = models.ManyToManyField(ActionGroup, blank=True)

    class Meta:
        verbose_name = u'Дилер'
        verbose_name_plural = u'Дилеры'
        ordering = ['name']

    def __unicode__(self):
        return u'{0}'.format(self.name)


class Client(models.Model):
    """ Клиенты (копии программы км-клиент)
    """
    dealer = models.ForeignKey(Dealer, related_name='clients',
                               verbose_name=u'Дилер')
    uuid = models.UUIDField(u'UUID', unique=True)
    login = models.CharField(u'Логин', max_length=255, blank=True, null=True)
    description = models.TextField(u'Описание', blank=True, null=True)
    create_date = models.DateTimeField(u'Дата создания', auto_now_add=True)
    change_date = models.DateTimeField(u'Дата изменения', auto_now=True)
    os = models.CharField(u'ОС', max_length=255, blank=True, null=True)
    ip = models.GenericIPAddressField(u'IP адрес', blank=True, null=True)
    user_name = models.CharField(u'Имя пользователя', max_length=255,
                                 blank=True, null=True)
    computer_name = models.CharField(u'Имя компьютера', max_length=255,
                                     blank=True, null=True)
    domain = models.CharField(u'Домен', max_length=255, blank=True, null=True)
    is_block = models.BooleanField(u'Заблокирован', default=False)
    history = HistoricalRecords()

    class Meta:
        verbose_name = u'КМ-клиент'
        verbose_name_plural = u'КМ-клиенты'

    def __unicode__(self):
        return u'{0}'.format(self.login)


class ClientActionLog(models.Model):
    """ Лог событий км-клиента (Client)
    """
    client = models.ForeignKey(Client, related_name='actions',
                               verbose_name=u'КМ-клиент')
    action = models.ForeignKey(Action, verbose_name=u'Событие')
    params = JSONField(u'Параметры', blank=True, null=True)
    date = models.DateTimeField(u'Дата события')

    class Meta:
        verbose_name = u'Событие КМ-клиента'
        verbose_name_plural = u'События КМ-клиента'
        ordering = ['-date']