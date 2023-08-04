from django.contrib import admin
from .models import Customer

#admin.site.register(Customer)
# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    '''Admin View for Customer'''

    list_display = ('user_name','email','is_active')
    list_filter = ('is_active')
    
    readonly_fields = ('email')
    search_fields = ('user_name')
    