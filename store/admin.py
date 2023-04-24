from django.contrib import admin

from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','category','Balance', 'price', 'pdf','Status')
    list_filter = ('name',"price")
    search_fields = ('price','category')
    
    list_editable = ('pdf','Balance','price','Status')

    prepopulated_fields ={'slug': ('name',)}