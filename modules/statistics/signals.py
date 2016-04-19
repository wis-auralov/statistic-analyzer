# -*- coding: utf-8 -*-

import logging
from django.dispatch import receiver
from django.dispatch import Signal
from django.db.models.signals import pre_save

from statistics.models import Client, Dealer
from kmclient.models import ApplicationBlacklist, User as KmClientDealer

log = logging.getLogger(__name__)

client_login_action = Signal(providing_args=['client_uuid', 'dealer_uname',
                                             'dealer_pass', 'params'])


@receiver(client_login_action)
def create_or_update_client(sender, **kwargs):
    """ Создаёт или обновляет Client на основе события авторизации
    :param kwargs: содержит client_uuid и params (поля модели Client)
    client_uuid - uuid клиента
    формат params = {
        "dealer_uuid": "2962134c-b1f8-11e2-93f1-002655df3ac1",
        "dealer_name": "-ГУРД А А  (дилерМСК)",
        "client_login": "гурда5",
        "client_home_path": "\\Users\\Николай",
        "client_os": "Windows_NT",
        "client_user_name": "Николай",
        "client_computer_name": "WIN7-NIX-VBOX",
        "client_domain": "WIN7-NIX-VBOX"
    }
    """
    dealer_uuid = kwargs['params'].get('dealer_uuid')
    if not dealer_uuid:
        kmclient_dealer_errors = (
            KmClientDealer.DoesNotExist, KmClientDealer.MultipleObjectsReturned
        )
        try:
            dealer_uuid = KmClientDealer.objects.get(
                uname=kwargs['dealer_uname'], pass_field=kwargs['dealer_pass']
            ).uuid
        except kmclient_dealer_errors as e:
            log.error(u'Error: {0}; Param: {1}'.format(e.message, str(kwargs)))
            return

    dealer, created = Dealer.objects.get_or_create(uuid=dealer_uuid)

    if created:
        try:
            dealer.name = kwargs['params']['dealer_name']
            dealer.save()
        except AttributeError:
            pass

    client, created = Client.objects.get_or_create(uuid=kwargs['client_uuid'],
                                                   dealer=dealer)
    updated = False
    for key, value in kwargs['params'].iteritems():
        if key.startswith('client_'):
            key = key.replace('client_', '')
            try:
                if getattr(client, key) != value:
                    setattr(client, key, value)
                    updated = True
            except AttributeError:
                continue

    if updated:
        client.save()


@receiver(pre_save, sender=Client)
def client_is_block(sender, instance, **kwargs):
    """ Блокирует экземпляр км-клиента в БД kmclient8 """
    try:
        old_instance = Client.objects.get(pk=instance.pk)
    except Client.DoesNotExist:
        return

    if old_instance.is_block != instance.is_block:
        query_kwargs = {
            'user_uuid': instance.dealer.uuid,
            'application_uuid': instance.uuid,
        }

        if instance.is_block:
            ApplicationBlacklist.objects.get_or_create(**query_kwargs)
        else:
            ApplicationBlacklist.objects.filter(**query_kwargs).delete()
