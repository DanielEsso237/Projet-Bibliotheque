from django.contrib import admin
from .models import SystemSettings

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'notifications_enabled',
        'updated_at'
    )
    fieldsets = (
        ('Préférences de Notification', {
            'fields': ('notifications_enabled',)
        }),
    )