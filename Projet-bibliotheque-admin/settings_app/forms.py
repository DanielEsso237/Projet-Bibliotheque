from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import SystemSettings
from users.models import CustomUser

class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = ['notifications_enabled']
        labels = {
            'notifications_enabled': 'Activer les notifications',
        }
        widgets = {
            'notifications_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

class UserProfileForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']
        labels = {
            'username': 'Nom d\'utilisateur',
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Adresse email',
            'phone_number': 'Numéro de téléphone',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'adresse@email.com',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+237 6XX XXX XXX',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre certains champs non modifiables si nécessaire (ex. email unique)
        self.fields['email'].required = True