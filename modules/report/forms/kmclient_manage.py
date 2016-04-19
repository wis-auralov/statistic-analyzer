# -*- coding: utf-8 -*-

from django import forms
from django.forms.formsets import formset_factory
from django.contrib.admin.widgets import AdminDateWidget, \
    FilteredSelectMultiple
from statistics.models import Action, Dealer
from report.data_collection import PERIOD_TYPE_CHOICE


class KmClientManagerForm(forms.Form):
    """Форма фильтрации данных для получения отчета

    CLIENT_FILTER_FIELDS - набор полей, которые соответствуют полям из модели
                           Client (названия ДОЛЖНЫ СОВПАДАТЬ)
    порядок следования полей формы (login, user_name, computer_name) определяет
    порядок зависимостей при подгрузке чойсов на страницу

    """
    CLIENT_FILTER_FIELDS = ('login', 'user_name', 'computer_name')

    date_from = forms.DateField(label=u'Дата от', widget=AdminDateWidget)
    date_to = forms.DateField(label=u'Дата до', widget=AdminDateWidget)
    period_type = forms.ChoiceField(choices=PERIOD_TYPE_CHOICE,
                                    label=u'Группировка')
    amount_of_pc = forms.IntegerField(label=u'Доступ с .. и более компьютеров',
                                      required=False, min_value=0)
    dealer = forms.ModelMultipleChoiceField(
        Dealer.objects.order_by('name'), label=u'Дилер', required=False,
        widget=FilteredSelectMultiple(u'Дилеры', is_stacked=False)
    )

    login = forms.MultipleChoiceField(label=u'Логин', required=False)
    user_name = forms.MultipleChoiceField(
        label=u'Имя пользователя', required=False
    )
    computer_name = forms.MultipleChoiceField(
        label=u'Имя компьютера', required=False
    )

    def clean_period_type(self):
        return int(self.cleaned_data['period_type'])

    def __init__(self, *args, **kwargs):
        # Выборка чойсов для полей в виде словаря ключ - название поля:
        # {'login': [('a','a'),('b','b')] ... }
        filter_choices = kwargs.pop('filter_choices', None)

        super(KmClientManagerForm, self).__init__(*args, **kwargs)

        # Устанавливаем для дополнительных полей фильтра css классы
        for field_name in self.CLIENT_FILTER_FIELDS:
            self.fields[field_name].widget.attrs['class'] = \
                'client_filter_fields'

        # Инициализируем чойсы для полей на основе тех данных, что переданы в
        # параметрах
        if filter_choices and isinstance(filter_choices, dict):
            for field_name, choices in filter_choices.iteritems():
                self.fields[field_name].choices = choices

    class Media(object):
        js = ('report/js/extended_filtering.js',)


class ActionForm(forms.Form):
    negative = forms.BooleanField(label=u'Не', required=False)
    action = forms.MultipleChoiceField(
        choices=Action.objects.order_by('name').values_list('id', 'name'),
        label=u'Событие',
        required=True,
    )
    UNION_AND = 'and'
    UNION_OR = 'or'
    UNION_CHOICE = (
        (UNION_AND, u'И'),
        (UNION_OR, u'Или')
    )
    union_type = forms.ChoiceField(
        choices=UNION_CHOICE,
        initial='and',
        label=u'Соединение',
    )

    class Media(object):
        js = ('report/js/formset.js',)

ActionFormset = formset_factory(ActionForm)