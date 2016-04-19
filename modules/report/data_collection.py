# -*- coding: utf-8 -*-
import os
import datetime
import django
import calendar
import logging
from collections import OrderedDict
from dateutil import relativedelta

from django.db.models import Count

from report.xlsx import XLSXSimple

log = logging.getLogger(__name__)

BY_DAY = 1
BY_WEEK = 2
BY_MONTH = 3

PERIOD_TYPE_CHOICE = (
    (BY_DAY, u'День'),
    (BY_WEEK, u'Неделя'),
    (BY_MONTH, u'Месяц'),
)


def get_date_periods(dt_start, dt_end, period_type):
    """Формирует набор с диапозонами дат (по указаной периодичности)

    :param dt_start: дата начала периода
    :param dt_end: дата окончания периода
    :param period_type: тип периода BY_DAY | BY_WEEK | BY_MONTH
    :return: словарь вида {
            'collection_header': ['1.12', '2.12', '3.12', '4.12'],
            'collection_set': [
                (date_start <datetime.date>, date_end<datetime.date>), ...
            ]
        }
    """
    cal = calendar.Calendar()
    rel_delta = relativedelta.relativedelta(dt_end, dt_start)
    periods_collection = []
    days_by_months = [
        (dt_start + relativedelta.relativedelta(months=x))
        for x in range(0, rel_delta.months+1)
    ]

    # 1 период по дням
    if period_type == BY_DAY:
        tmp_list = [dt_start + datetime.timedelta(days=x)
                    for x in range(0, (dt_end-dt_start).days)]
        periods_collection = [(date_item, date_item) for date_item in tmp_list]

    # 2 период по неделям
    elif period_type == BY_WEEK:
        periods_collection = list()
        for date_item in days_by_months:
            periods_collection.extend(
                [
                    (week[0], week[6]) for week in
                    cal.monthdatescalendar(date_item.year, date_item.month)
                    if (dt_start-week[0]).days <= 6 and
                    (week[6] - dt_end).days <= 6
                ]
            )

    # 3 период по месяцам
    elif period_type == BY_MONTH:
        periods_collection = [
            (
                datetime.date(date_item.year, date_item.month, 1),
                datetime.date(
                    date_item.year, date_item.month,
                    calendar.monthrange(date_item.year, date_item.month)[1]
                )
            )
            for date_item in days_by_months
        ]

    result_dict = {
        'collection_header': [
            period_item[0].strftime('%d.%m')
            if period_type == BY_DAY else
            '{0} - {1}'.format(
                period_item[0].strftime('%d.%m'),
                period_item[1].strftime('%d.%m')
            )
            for period_item in periods_collection
        ],
        'collection_set': periods_collection
    }
    return result_dict


def check_date_for_group(checking_date, period_list):
    """Проверяет приналдежность даты к одному из периодов

    :param checking_date: проверяемая дата
    :param period_list: массив из периодов дат [(dt_start, dt_end),...]
    :return: индекс в period_list массиве
    """

    result_index = -1
    for index, date_tuple in enumerate(period_list):
        if checking_date > date_tuple[1]:
            continue
        if checking_date >= date_tuple[0]:
            result_index = index
            break
    else:
        log.warning(
            'Not found time_group for date [{0}] in time_groups:[{1}]'.format(
                checking_date, period_list
            )
        )
    return result_index


def get_collection_items(client_action_logs, dt_start, dt_end, date_period_type):
    """Формирует набор операций с детализацией количества по
    временным периодам и группировкой по дилерам, логинам и операциям

    :param client_action_logs: набор акшн логов которые нужно сгруппировать
    :param dt_start: дата начала периода
    :param dt_end: дата окончания периода
    :param date_period_type: тип периода для группировки
                             BY_DAY|BY_WEEK|BY_MONTH
    :return:  словарь вида
        result = {
            'dates_period_header' : ['1.12', '2.12', '3.12', '4.12'],
            'collection_set':{
                u'-БЕЛЯКЕВИЧ(дилер)': {   # имя дилера
                    'id': 410, # уникальный id в нашей базе
                    'logins':{
                        u'Belyakevich':{ # login_name
                            'client_ids': {
                                '1642':{
                                    'user_name': 'Вася',
                                    'computer_name': 'vasya-pc',
                                    'create_date': '27.01.2016',
                                    'uuid':3838cd3b25b1472199a8f6210ec23475,
                                    'actions':{
                                        u'Операция 1': { # action_name
                                            'total_count': 24,
                                            'details_count': [12, 0, 2, 10]
                                            # детализация количестка операций
                                            (индексы сооответствуют набору
                                            dates_period_header)
                                        }
                                    }
                                }
                            }
                        },
                        u'Компьютер 2':{
                            'client_ids': {
                                '1643':{
                                    'uuid':3838cd3b25b1472199a8f6210ec23466,
                                    'actions': {
                                        u'Операция 23': {
                                            'total_count': 240,
                                            'details_count': [12, 0, 2, 10]
                                        }
                                    }

                                }
                            }
                        }
                    }
                }
            }
        }

    """
    # Формируем сгруппированные записи для формирования структуры
    grouped_action_log = list(client_action_logs.values(
        'client__login', 'client_id', 'client__uuid', 'action__name',
        'client__dealer__name', 'client__dealer_id', 'client__user_name',
        'client__computer_name', 'client__ip', 'client__domain',
        'client__create_date',
    ).order_by('action__name').annotate(Count('action')))

    # Подготавливаем данные для из подсчета
    client_actions_list = list(client_action_logs.extra(
        select={'action_date': 'DATE(date at TIME ZONE \'Europe/Moscow\')'}
    ).values(
        'client__login', 'client_id', 'action__name',
        'client__dealer__name', 'action_date'
    ))

    collection_set = {}
    # Формируем древовидный словарь для данных
    date_periods = get_date_periods(dt_start, dt_end, date_period_type)
    for log_entry in grouped_action_log:
        d_name = log_entry['client__dealer__name']
        d_id = log_entry['client__dealer_id']
        client_login = log_entry['client__login']
        client_id = log_entry['client_id']
        client_uuid = log_entry['client__uuid']
        action_name = log_entry['action__name']

        collection_set.setdefault(d_name, {'id': d_id, 'logins': {}})
        collection_set[d_name]['logins'].setdefault(client_login,
                                                    {'client_ids': {}})
        collection_set[d_name]['logins'][client_login]['client_ids']\
            .setdefault(client_id, {
                'uuid': client_uuid,
                'user_name': log_entry['client__user_name'],
                'computer_name': log_entry['client__computer_name'],
                'ip': log_entry['client__ip'],
                'domain': log_entry['client__domain'],
                'create_date': log_entry['client__create_date'],
                'actions': OrderedDict()})
        collection_set[d_name]['logins'][client_login]['client_ids']\
            [client_id]['actions'].setdefault(
                action_name,
                {
                    'total_count': log_entry['action__count'],
                    'details_count': [0]*len(date_periods['collection_set'])
                }
        )

    # Заполняем полученный словарь и сетку в нем количеством найденных записей
    for action_log in client_actions_list:
        try:
            time_group_index = check_date_for_group(
                action_log['action_date'], date_periods['collection_set']
            )
            collection_set[action_log['client__dealer__name']]\
                ['logins'][action_log['client__login']]\
                ['client_ids'][action_log['client_id']]\
                ['actions'][action_log['action__name']]\
                ['details_count'][time_group_index] += 1

        except KeyError:
            pass

    return {
        'dates_period_header': date_periods['collection_header'],
        'collection_set': collection_set
    }


def generate_xlsx(collection_data):
    """ Подготавливает csv на основе данных из collection_data

    :param collection_data: словарь с данными для отчета
    :return: csv response
    """
    fields_data = list()
    collection_set = collection_data['collection_set']
    for dealer_key, dealer_value in collection_set.iteritems():
        for login_key, login_value in dealer_value['logins'].iteritems():
            for client_id, client_value in \
                    login_value['client_ids'].iteritems():
                for action_key, action_value in \
                        client_value['actions'].iteritems():
                    item_arr = [dealer_key,
                                login_key,
                                str(client_value['uuid']),
                                client_value['user_name'],
                                client_value['computer_name'],
                                client_value['ip'],
                                client_value['domain'],
                                client_value['create_date'],
                                action_key,
                                action_value['total_count']]
                    item_arr.extend(action_value['details_count'])
                    fields_data.append(item_arr)
    fields_header = [u'Дилер', u'Логин', u'UUID клиента', u'Имя пользователя',
                     u'Имя компьютера', u'IP', u'Домен', u'Дата создания',
                     u'Вид операции', u'Количество Итого']
    fields_header.extend(collection_data['dates_period_header'])
    xlsx = XLSXSimple(u'отчет по дилерам', fields_header, fields_data)
    book = xlsx.get_work_book()
    return book


if __name__ == '__main__':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    django.setup()
    from statistics.models import ClientActionLog

    start_dt = datetime.date(2015, 12, 21)
    end_dt = datetime.date(2015, 12, 31)
    client_logs = ClientActionLog.objects.filter(
        client__isnull=False, date__gte=start_dt, date__lte=end_dt
    )
    result = get_collection_items(client_logs, dt_start=start_dt,
                                  dt_end=end_dt, date_period_type=BY_WEEK)

    work_book = generate_xlsx(result)
    work_book.save('/tmp/test.xlsx')
    print work_book
