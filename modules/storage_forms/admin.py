# -*- coding: utf-8 -*-

from django.contrib import admin
from django.core.urlresolvers import reverse

from storage_forms.models import StoredFormCollection


class StoredFormCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'link_to_use')
    fields = ('name', 'description')
    actions = None

    def link_to_use(self, instance):
        url = reverse(instance.report_type)
        get_params = 'stored_form={0}'.format(instance.pk)
        return u'<a href="{0}?{1}"> Использовать сохраненную форму ' \
               u'"{2}"</a>'.format(url, get_params, instance.name)

    link_to_use.short_description = u"Действия"
    link_to_use.allow_tags = True


admin.site.register(StoredFormCollection, StoredFormCollectionAdmin)
