from django.contrib import admin
from .models import Customer

# Register your models here.
@admin.register(Customer)
class Admin(admin.ModelAdmin):
    list_display = ('email','user_name','is_active')
    list_filter = ('is_active')
    search_fields = ('user_name','email')
    
    list_editable = ('is_active')
