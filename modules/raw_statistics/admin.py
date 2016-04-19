# -*- coding: utf-8 -*-

from django.contrib import admin

from raw_statistics.models import RawClientActionLog


class RawClientActionLogAdmin(admin.ModelAdmin):
    list_display = ('client_uuid', 'action_uuid', 'date', 'processing_error')
    search_fields = ('client_uuid', 'action_uuid')
    list_filter = ('processing_error', )

    actions = ['mark_as_for_processing']

    def mark_as_for_processing(self, request, queryset):
        queryset.update(processing_error=False)
    mark_as_for_processing.short_description = u'Пометить для обработки'


admin.site.register(RawClientActionLog, RawClientActionLogAdmin)

