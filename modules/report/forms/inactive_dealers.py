# -*- coding: utf-8 -*-
from django.contrib.admin.widgets import AdminDateWidget
from django import forms


class InactiveDealersForm(forms.Form):
    """ Форма отчёта Неактивные дилеры
    """
    date_from = forms.DateField(label=u'Дата от', widget=AdminDateWidget)
    date_to = forms.DateField(label=u'Дата до', widget=AdminDateWidget)