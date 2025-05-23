from django import forms
from .models import SystemSettings

class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = ['notification_cleanup_days']
        widgets = {
            'notification_cleanup_days': forms.Select(choices=[
                (15, '15 jours'),
                (30, '30 jours'),
                (60, '60 jours'),
            ]),
        }