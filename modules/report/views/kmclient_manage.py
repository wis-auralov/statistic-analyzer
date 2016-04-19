# -*- coding: utf-8 -*-
import json

from django.conf import settings
from django.http.response import HttpResponse
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from django.db.models import Q, Count

from storage_forms.views import StorageFormMixin
from helpers import BaseApiView, API_OK, API_ERROR
from report.forms.kmclient_manage import (
    KmClientManagerForm, ActionFormset, ActionForm
)
from statistics.models import ClientActionLog, Client, Dealer
from report.data_collection import get_collection_items, generate_xlsx


def get_client_filter_choices(filter_data):
    """Метод позволяет на основе данных для отбора клиентов выбрать чойсы для
    полей фильтра. в результате формируем словарь с готовыми чойсами:
    {
        'choices': {
            'login': [('admin', 'admin'), ('pupkin', 'pupkin')],
            'user_name': [('vasya', 'vasya')],
            'computer_name': [('pupkin-pc', 'pupkin-pc')]
        }
    }

    :param filter_data: словарь с параметрами для выборки {'login': 'Test'}
    :return: словарь значений
    """

    query = Q()
    for field_name in KmClientManagerForm.CLIENT_FILTER_FIELDS:
        if filter_data.get(field_name, None):
            q_params = {'{0}__in'.format(field_name): filter_data[field_name]}
            query &= Q(**q_params)

    if 'dealer' in filter_data:
        query &= Q(dealer_id__in=filter_data['dealer'])

    client_qs = list(Client.objects.filter(query).values(
        *KmClientManagerForm.CLIENT_FILTER_FIELDS)
    )

    result_dict = {'choices': {}}
    for field_name in KmClientManagerForm.CLIENT_FILTER_FIELDS:
        result_dict['choices'][field_name] = list(set(
            [(client[field_name], client[field_name]) for client in client_qs]
        ))
        result_dict['choices'][field_name].sort()

    return result_dict


class KmClientManagerView(FormMixin, StorageFormMixin, ListView):
    template_name = 'report/kmclient_manage.html'
    form_class = KmClientManagerForm
    formset_class = ActionFormset
    object_list = None  # список Клиентов (модель Client)
    current_stored_form = None
    report_type = settings.REPORT_TYPE_ACTIVE_DEALERS

    def get_queryset(self):
        return Client.objects.select_related('dealer')

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)

    @staticmethod
    def get_formset_action_filter(formset):
        """ Получение фильтра на основе formset_action
        :param formset: набор форм action
        :return: фильтер Q
        """
        action_filter = Q()
        # соединение форм идёт в обратном порядке, так как union_type
        # первой формы должен использоваться для соединения со второй
        for action_form_data in reversed(formset.cleaned_data):
            if not action_form_data:
                # если форма пуста - пропускаем её
                continue

            action_in = Q(actions__action__in=action_form_data['action'])

            if action_form_data['union_type'] == ActionForm.UNION_AND:
                action_filter &= ~action_in if action_form_data['negative'] \
                    else action_in
            elif action_form_data['union_type'] == ActionForm.UNION_OR:
                action_filter |= ~action_in if action_form_data['negative'] \
                    else action_in

        return action_filter

    def filter_client_list(self, client_queryset, form, formset):
        """ Фильтрует клиентов по данным из формы
        :param form: форма
        :param formset: формсет
        :return:
        """
        form_data = form.cleaned_data
        query_params = dict()
        query_params['actions__date__range'] = (
            form_data['date_from'], form_data['date_to']
        )
        # подкидываем в фильтр выборки дополнительные поля фильтров
        if form_data['dealer']:
            query_params['dealer__in'] = form_data['dealer']
        for field in KmClientManagerForm.CLIENT_FILTER_FIELDS:
            if form_data[field]:
                query_params['{0}__in'.format(field)] = form_data[field]
        filtered_clients = client_queryset.filter(
            self.get_formset_action_filter(formset),
            **query_params
        ).distinct()

        if form_data['amount_of_pc']:
            # выбираем только тех клиентов, которые под одним логином заходят
            # с N и более компов
            client_ids = list(set(
                filtered_clients.values_list('id', flat=True)
            ))
            client_pc_counts = Client.objects.filter(id__in=client_ids).values(
                'login', 'dealer_id'
            ).annotate(pc_count=Count('login')).filter(
                pc_count__gte=form_data['amount_of_pc']
            )
            dealer_ids = [
                client_pc_count['dealer_id']
                for client_pc_count in client_pc_counts
            ]
            filtered_clients = filtered_clients.filter(
                dealer_id__in=dealer_ids
            )

        # формируем отчёт по всем дилерам (по всем клиентам для этих дилеров),
        # клиенты которых попадают под условие фильтрации формы
        filtered_dealers = Dealer.objects.filter(clients__in=filtered_clients)

        return Client.objects.filter(dealer__in=filtered_dealers)

    @staticmethod
    def get_collection_data(client_queryset, form):
        """ Возвращает набор операций с детализацией количества по временным периодам
        :param form:
        :return: словарь со значениями метода get_collection_items
        """
        form_data = form.cleaned_data
        client_action_logs = ClientActionLog.objects.filter(
            client__in=client_queryset, date__gte=form_data['date_from'],
            date__lte=form_data['date_to']
        )
        collection_items = get_collection_items(
            client_action_logs,
            dt_start=form_data['date_from'],
            dt_end=form_data['date_to'],
            date_period_type=form_data['period_type'],
        )

        return collection_items

    def post(self, request, *args, **kwargs):
        main_form_kwargs = self.get_form_kwargs()
        # Получаем чойсы по полям клиента для дополнительной фильтрации
        client_filter_data = get_client_filter_choices(
            {'dealer': request.POST.getlist('dealer')}
        )
        # расширяем поля формы сформированными чойсами (для валидации и
        # оторажения пользователю)
        main_form_kwargs.update({
            'filter_choices': client_filter_data['choices']
        })
        form = self.form_class(**main_form_kwargs)
        formset = self.formset_class(**self.get_form_kwargs())
        collection_data = {}
        self.object_list = self.get_queryset()

        if form.is_valid() and formset.is_valid():
            # TODO: подумать над разбиением метода,
            # в данный момент сюда интегрирована логика из StorageFormMixin
            action_triggered, store_result = self.store_form_by_action(
                request, form=form, formset=formset
            )
            if isinstance(store_result, HttpResponse):
                return store_result

            if not action_triggered:
                request_action = request.POST.get('action')
                self.object_list = self.filter_client_list(
                    self.object_list, form, formset
                )
                collection_data = self.get_collection_data(
                    self.object_list, form
                )

                if request_action == 'gen_XLSX':
                    workbook = generate_xlsx(collection_data)
                    response = HttpResponse(
                        content_type="application/vnd.ms-excel"
                    )
                    response['Content-Disposition'] = \
                        'attachment; filename="report.xlsx"'
                    workbook.save(response)

                    return response

        context = self.get_context_data(form=form, formset=formset)
        context.update(collection_data)

        return self.render_to_response(context)


class GenerateFilterChoicesApi(BaseApiView):
    """
    Класс API, которое будет возвращать в зависимости от параметров -
    значения для фильтров отчета
        формат ответа:
         {
            'status': 'OK',
            'message':'',
            'data': {
                'login': ['log1',  'log2', 'log3'],
                'user_name': ['user1', 'user2']
                'computer_name': ['pc1',  'pc2', 'pc3'],
                ...
            }
         }
    """

    def post(self, *args, **kwargs):
        request = args[0]

        try:
            filter_data = json.loads(request.body.decode('utf-8', 'ignore'))
        except Exception as err:
            return self.get_response(status=API_ERROR, message=err.message)

        client_filter_data = get_client_filter_choices(filter_data)
        data = {}
        for field_name in KmClientManagerForm.CLIENT_FILTER_FIELDS:
            data[field_name] = client_filter_data['choices'][field_name]

        return self.get_response(status=API_OK, data=data)
