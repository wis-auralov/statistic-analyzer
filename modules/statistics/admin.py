# -*- coding: utf-8 -*-

from django.contrib import admin
from django.http.response import HttpResponse
from simple_history.admin import SimpleHistoryAdmin

from report.xlsx import XLSXFromQueryset
from statistics.models import (
    Client, Dealer, Action, ActionGroup, ClientActionLog
)


class ClientAdmin(SimpleHistoryAdmin):
    list_display = ('login', 'dealer', 'uuid', 'ip', 'computer_name',
                    'user_name', 'change_date')
    search_fields = ('uuid', 'login', 'ip', 'dealer__name', 'dealer__uuid')
    list_filter = ('is_block', )
    date_hierarchy = 'change_date'
    readonly_fields = (
        'dealer', 'uuid', 'login', 'os', 'ip', 'user_name', 'computer_name',
        'domain', 'create_date', 'change_date',
    )
    fields = (
        'dealer', 'login', 'uuid', 'description', 'is_block', 'os', 'ip',
        'user_name', 'computer_name', 'domain', 'create_date', 'change_date',
    )

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ('create_date', 'change_date', )
        else:
            return super(ClientAdmin, self).get_readonly_fields(request, obj)


class DealerAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid')
    search_fields = ('name', 'uuid')
    readonly_fields = ('name', 'uuid',)
    fields = ('name', 'uuid', 'action_logging', 'action_group_logging')


class ActionAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid')
    list_filter = ('action_group', )
    search_fields = ('name', 'uuid')
    readonly_fields = ('uuid', )
    fields = ('uuid', 'name', 'action_group',)


class ActionGroupAdmin(admin.ModelAdmin):
    list_display = ('name', )


class ClientActionLogAdmin(admin.ModelAdmin):
    list_display = ('client', 'get_client_uuid', 'action', 'date')
    list_filter = ('action', 'action__action_group')
    search_fields = ('client__login', 'client__uuid')
    date_hierarchy = 'date'

    def get_client_uuid(self, obj):
        return obj.client.uuid
    get_client_uuid.short_description = u'UUID км-клиента'


def export_as_xlsx(modeladmin, request, queryset):
    workbook = XLSXFromQueryset(fields_data=queryset).get_work_book()
    response = HttpResponse(content_type="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename="{0}.xlsx"'\
        .format(modeladmin.model._meta.model_name)
    workbook.save(response)

    return response


admin.site.register(Client, ClientAdmin)
admin.site.register(Dealer, DealerAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(ActionGroup, ActionGroupAdmin)
admin.site.register(ClientActionLog, ClientActionLogAdmin)

admin.site.add_action(export_as_xlsx, u'Экспортировать в Excel')
admin.site.disable_action('delete_selected')