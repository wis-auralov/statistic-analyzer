# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms import forms
from django.http.response import Http404, HttpResponseRedirect

from storage_forms.models import StoredFormCollection

log = logging.getLogger(__name__)


class StorageFormMixin(object):
    """Миксин к вьюхе и форм-миксину добавляет методы для работы с сохраненными
    в базу данных формами

    """
    formset_class = None
    form_class = None
    current_stored_form = None
    report_type = None
    request = None

    def __init__(self, *args, **kwargs):
        if not self.form_class:
            raise NotImplementedError('Need set form_class')
        if self.report_type not in \
            [rep_choice[0] for rep_choice in settings.TYPE_REPORT_CHOICES]:
            raise NotImplementedError('report type must be one '
                                      'of settings.TYPE_REPORT_CHOICES')

    def get_form(self, *args, **kwargs):
        raise NotImplementedError('Class must be inherited from FormMixin')

    def get_form_kwargs(self, *args, **kwargs):
        raise NotImplementedError('Class must be inherited from FormMixin')

    def get_form_container(self, formset_class=None):
        """ Возвращает словарь с формой и формсетом, сохраненные в базе
        если формсет не указан в параметрах класса - возвращается словарь
        только с одной формы
        :param formset_class: кастомизированный класс формсета
        :return: {'form': форма, 'formset': формсет}
        """

        stored_form_pk = self.request.GET.get('stored_form')
        if stored_form_pk:
            try:
                self.current_stored_form = StoredFormCollection.objects.get(
                    pk=stored_form_pk
                )
            except:
                raise Http404

        form = formset = None
        formset_class = formset_class or self.formset_class
        if self.current_stored_form:

            form = self.current_stored_form.pickled_form
            formset_data = self.current_stored_form.pickled_formset
            if not isinstance(form, forms.Form):
                form = self.get_form()
                log.error(
                    'Not valid picled value (form) in StoredFormCollection '
                    'id=[{0}]'.format(self.current_stored_form.id)
                )

            if formset_class:
                if isinstance(formset_data, dict):
                    formset = formset_class(formset_data)
                else:
                    log.error(
                        'Not valid picled value (formset_data) in '
                        'StoredFormCollection id=[{0}]'.format(
                            self.current_stored_form.id
                        )
                    )

        result = {'form': form or self.get_form()}
        if formset_class:
            result['formset'] = formset or \
                                formset_class(**self.get_form_kwargs())

        return result

    def get_context_data(self, **kwargs):
        form_container = self.get_form_container()
        extra_context = {
            'stored_forms': StoredFormCollection.objects.filter(
                report_type=self.report_type
            ),
            'current_stored_form': self.current_stored_form
        }
        kwargs.update(extra_context)
        if self.request.method == 'GET':
            kwargs.update(form_container)
        return kwargs

    def store_form_by_action(self, request, form, formset=None):
        """ выполняет сохранение в базу только если пришел в реквесте нужный
        акшн
        :param request: реквест стандартный
        :param form:  сохраняемая форма
        :param formset:  формсет для сохраненния(не обязателен)
        :return: ("было выполнено какое-то действие", результат сохранения )

        """
        stored_form_pk = request.POST.get('stored_form_pk')
        request_action = request.POST.get('action')
        action_triggered = False
        store_result = None
        if request_action == 'save_form_as_new':
            store_result = self.store_form(form, formset, as_new=True)
            action_triggered = True
        elif request_action == 'save_form':
            store_result = self.store_form(
                form, formset, stored_form_pk=stored_form_pk,
                as_new=bool(not stored_form_pk)
            )
            action_triggered = True

        return action_triggered, store_result

    def store_form(self, form, formset=None, stored_form_pk=None, as_new=False):
        """ сохраняем форму в базе (новую или обновляем имеющуюся)

        :param form: сохраняемая форма
        :param formset: сохраняемый формсет
        :param stored_form_pk: id уже хранимой в базе формы (для обновления)
        :param as_new: флаг - сторим новую или пытаемся обновить?
        :return: редирект на страницу редактирования сохраненной формы если она
                 создалась. или ничего если просто обновили имеющуюся
        """
        if as_new:
            stored_form = StoredFormCollection(report_type=self.report_type)
        else:
            try:
                stored_form = StoredFormCollection.objects.get(
                    pk=stored_form_pk
                )
            except StoredFormCollection.DoesNotExist:
                raise Http404
        stored_form.pickled_form = form
        if formset:
            stored_form.pickled_formset = formset.data
        stored_form.save()
        if as_new:
            # если запрос на создание новой формы - редиректнуть на созданный
            # объект
            url_name = 'admin:{0}_{1}_change'.format(
                stored_form._meta.app_label, stored_form._meta.model_name
            )
            messages.info(
                self.request,
                u'Новая форма успешно сохранена в базе. Введите имя'
            )
            return HttpResponseRedirect(reverse(url_name,
                                                args=[stored_form.pk]))
        else:
            messages.info(
                self.request, u'Форма "{0}" успешно сохранена в базе.'.format(
                      stored_form.name
                )
            )
            return None
