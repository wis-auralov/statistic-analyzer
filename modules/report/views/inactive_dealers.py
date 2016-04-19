# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from report.xlsx import XLSXSimple

from statistics.models import Client
from kmclient.models import User as KmClientDealer
from report.forms.inactive_dealers import InactiveDealersForm


class InactiveDealersView(FormMixin, ListView):
    """ Отчёт по неактивным дилерам.

    С точки зрения заказчика неактивный дилер - это
    Доступ дилеру открыт, но с данной незаблокированной копии КМ-Клиента
    не выполняются действия.
    """
    template_name = 'report/inactive_dealers.html'
    form_class = InactiveDealersForm
    queryset = Client.objects.select_related('dealer').order_by('dealer__name')
    object_list = None

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_xlsx_workboork(self, queryset):
        return XLSXSimple(
            u'неактивные дилеры',
            (u'Дилер', u'Дилер UUID', u'Клиент', u'Клиент UUID'),
            queryset.values_list('dealer__name', 'dealer__uuid',
                                 'login', 'uuid')
        ).get_work_book()

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            form_data = form.cleaned_data            
            active_dealers_uuid = list(KmClientDealer.objects.filter(active=1)
                                       .values_list('uuid', flat=True))
            no_active_clients = self.get_queryset().filter(
                dealer__uuid__in=active_dealers_uuid
            ).exclude(actions__date__range=(
                form_data['date_from'], form_data['date_to']
            ))
            # из object_list данные попадут в контекст в
            # django.views.generic.list.MultipleObjectMixin#get_context_data
            self.object_list = no_active_clients

        if request.POST.get('action') == 'gen_XLSX' and self.object_list:
            workbook = self.get_xlsx_workboork(self.object_list)
            response = HttpResponse(content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'attachment; ' \
                                              'filename="report.xlsx"'
            workbook.save(response)

            return response

        context = self.get_context_data(form=form)
        return self.render_to_response(context)