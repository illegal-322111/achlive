from django.contrib import admin
from .models import *
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('status','product', 'order_id', 'address', 'btcvalue', 'received', 'sold', 'created_by','created_at')
    list_filter = ('sold',"received")
    search_fields = ('created_by','order_id')
    
    list_editable = ('sold','created_at','product')

    fieldsets = (
        (None, {
            'fields': ('status', 'order_id', 'address', 'btcvalue', 'received', 'product', 'created_by','created_at')
        }),
    )
admin.site.register(Invoice, InvoiceAdmin)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ('status', 'order_id', 'address', 'balance', 'received', 'created_by','created_at')
    
    search_fields = ('created_by__user_name',)
    
    list_editable = ('balance',)

    fieldsets = (
        (None, {
            'fields': ('status', 'order_id', 'address', 'btcvalue', 'received', 'balance', 'created_by','created_at')
        }),
    )
admin.site.register(Balance, BalanceAdmin)