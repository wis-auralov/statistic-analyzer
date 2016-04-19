# -*- coding: utf-8 -*-
from django import template

from report.data_collection import BY_DAY, BY_WEEK, BY_MONTH

register = template.Library()


@register.filter(is_safe=True)
def add_css_by_period(period_type):
    period_aliases = {
        BY_DAY: 'by-day',
        BY_WEEK: 'by-week',
        BY_MONTH: 'by-month'
    }
    if int(period_type) in period_aliases:
        return period_aliases[int(period_type)]
    else:
        return ''
