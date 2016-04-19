# -*- coding: utf-8 -*-

import logging
from app_celery import app

from raw_statistics.models import RawClientActionLog
from statistics.models import ClientActionLog, Client, Action

log = logging.getLogger(__name__)


@app.task(name='sync_statistics')
def sync_statistics():
    """ Перекачка данных из модели RawClientActionLog в ClientActionLog
    """
    client_by_uuid = {i.uuid: i for i in Client.objects.all()}
    action_by_uuid = {i.uuid: i for i in Action.objects.all()}

    raw_logs = RawClientActionLog.objects.filter(processing_error=False)[:1000]
    while raw_logs.exists():
        clients = []
        raw_log_ids = []

        for raw_log in raw_logs:
            try:
                clients.append(ClientActionLog(
                    client=client_by_uuid[raw_log.client_uuid],
                    action=action_by_uuid[raw_log.action_uuid],
                    params=raw_log.params,
                    date=raw_log.date,
                ))
                raw_log_ids.append(raw_log.id)
            except KeyError as e:
                raw_log.processing_error = True
                raw_log.save()
                log.error(
                    "UUID {0} does not exist. Client: {1}; Action: {2}; "
                    "Params: {3}; Date: {4};".format(
                        e.message, raw_log.client_uuid, raw_log.action_uuid,
                        raw_log.params, raw_log.date
                    )
                )

        ClientActionLog.objects.bulk_create(clients)
        RawClientActionLog.objects.filter(id__in=raw_log_ids).delete()
        raw_logs = RawClientActionLog.objects.filter(
            processing_error=False)[:1000]