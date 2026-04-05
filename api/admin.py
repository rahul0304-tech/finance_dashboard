from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FinancialRecord

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Management', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Management', {'fields': ('role',)}),
    )

class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'transaction_type', 'amount', 'category', 'date', 'is_deleted']
    list_filter = ['transaction_type', 'category', 'date', 'is_deleted']
    search_fields = ['category', 'notes']

admin.site.register(User, CustomUserAdmin)
admin.site.register(FinancialRecord, FinancialRecordAdmin)
