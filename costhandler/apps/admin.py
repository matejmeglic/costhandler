from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Pricelist, PricelistEntry, List, ListEntry

class PricelistAdmin(admin.ModelAdmin):
    list_display = ('id', 'pricelist_name', 'description', 'user', 'is_active', 'created_dt')
    list_filter = ('is_active', 'user')
    search_fields = ('pricelist_name', 'description', 'user__username')

class PricelistEntryAdmin(admin.ModelAdmin):
    list_display = ('id','item_name', 'group_name', 'pricelist', 'price', 'currency', 'unit', 'min_duration', 'created_dt')
    list_filter = ('group_name', 'pricelist__pricelist_name')
    search_fields = ('item_name', 'group_name', 'pricelist__pricelist_name')
    ordering = ('pricelist__pricelist_name', 'item_name')

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    list_display = ('id','username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

class ListAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'comment', 'extra_costs', 'extra_costs_currency', 'created_dt')
    list_filter = ('user', 'created_dt')
    search_fields = ('name', 'user__username', 'comment')
    ordering = ('created_dt', 'name')

class ListEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'list', 'pricelist_entry', 'quantity', 'extra_costs', 'total_cost', 'comment', 'person', 'created_dt')
    list_filter = ('list__name', 'pricelist_entry__item_name', 'created_dt')
    search_fields = ('list__name', 'pricelist_entry__item_name', 'person', 'comment')
    ordering = ('created_dt', 'list__name')

    def total_cost(self, obj):
        return obj.total_cost  # Call the property to display total cost in admin
    total_cost.short_description = 'Total Cost'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Pricelist, PricelistAdmin)
admin.site.register(PricelistEntry, PricelistEntryAdmin)

admin.site.register(List, ListAdmin)
admin.site.register(ListEntry, ListEntryAdmin)
