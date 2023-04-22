from django.contrib import admin
from .models import *
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('status', 'order_id', 'address', 'btcvalue', 'received', 'sold', 'created_by','created_at')
    list_filter = ('status','sold')
    search_fields = ('created_by')
    
    list_editable = ('status','sold','created_at')

    fieldsets = (
        (None, {
            'fields': ('status', 'order_id', 'address', 'btcvalue', 'received', 'balance', 'created_by','created_at')
        }),
    )
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Balance)