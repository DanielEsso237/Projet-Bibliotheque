from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class LibrarianRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Entrez un nom d’utilisateur'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Entrez votre email'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Entrez votre numéro (optionnel)'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Entrez un mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmez votre mot de passe'})

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'phone_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_librarian = True  # Force le rôle à bibliothécaire
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data
class LibrarianLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']