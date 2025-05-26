from django.contrib import admin
from .models import SystemSettings

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'notification_cleanup_days',
        'low_stock_threshold',
        'loan_warning_days',
        'loan_overdue_days',
        'max_loans_per_user',
        'loan_duration',
        'critical_stock_threshold',
        'updated_at'
    )
    fieldsets = (
        ('Paramètres des stocks', {
            'fields': ('low_stock_threshold', 'critical_stock_threshold')
        }),
        ('Paramètres des prêts', {
            'fields': ('loan_warning_days', 'loan_overdue_days', 'max_loans_per_user', 'loan_duration')
        }),
        ('Paramètres des notifications', {
            'fields': ('notification_cleanup_days',)
        }),
    )