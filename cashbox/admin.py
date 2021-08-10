from django.contrib import admin

from cashbox.models import *


class CashBoxAdmin(admin.ModelAdmin):
    list_display = ['user', 'method', 'operator', 'props_number', 'amount', 'is_paid', 'create_at']
    list_display_links = list_display
    list_filter = ['method', 'operator', 'is_paid']


class TransferAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'amount', 'code', 'is_paid', 'is_read', 'create_at']
    list_display_links = list_display
    list_filter = ['sender', 'receiver', 'is_paid']


class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'create_at']
    list_display_links = list_display
    list_filter = ['user']
    search_fields = ['code']


admin.site.register(CashBox, CashBoxAdmin)
admin.site.register(Transfer, TransferAdmin)
admin.site.register(PromoCode, PromoCodeAdmin)
