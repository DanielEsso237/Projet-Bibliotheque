from django import forms
from .models import SystemSettings

class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = [
            'notification_cleanup_days',
            'low_stock_threshold',
            'loan_warning_days',
            'loan_overdue_days',
            'max_loans_per_user',
            'loan_duration',
            'critical_stock_threshold'
        ]
        labels = {
            'notification_cleanup_days': 'Durée de conservation des notifications supprimées (jours)',
            'low_stock_threshold': 'Seuil de stock faible',
            'loan_warning_days': 'Jours pour alerte de retour proche',
            'loan_overdue_days': 'Délai pour alerte de retard (jours)',
            'max_loans_per_user': 'Nombre maximum de prêts par utilisateur',
            'loan_duration': 'Durée standard d’un prêt (jours)',
            'critical_stock_threshold': 'Seuil de stock critique'
        }
        widgets = {
            'notification_cleanup_days': forms.Select(choices=[
                (15, '15 jours'), (30, '30 jours'), (60, '60 jours')
            ]),
            'low_stock_threshold': forms.Select(choices=[
                (1, '1 unité'), (3, '3 unités'), (5, '5 unités'), (10, '10 unités')
            ]),
            'loan_warning_days': forms.Select(choices=[
                (1, '1 jour'), (2, '2 jours'), (3, '3 jours'), (5, '5 jours')
            ]),
            'loan_overdue_days': forms.Select(choices=[
                (0, 'Immédiat'), (1, '1 jour'), (2, '2 jours')
            ]),
            'max_loans_per_user': forms.Select(choices=[
                (1, '1 prêt'), (3, '3 prêts'), (5, '5 prêts'), (10, '10 prêts')
            ]),
            'loan_duration': forms.Select(choices=[
                (7, '7 jours'), (14, '14 jours'), (21, '21 jours'), (30, '30 jours')
            ]),
            'critical_stock_threshold': forms.Select(choices=[
                (0, '0 unité'), (1, '1 unité'), (2, '2 unités')
            ]),
        }