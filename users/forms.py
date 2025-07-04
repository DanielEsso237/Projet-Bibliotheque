from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser
from django.contrib.auth import get_user_model

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
        user.user_type = 'LIBRARIAN'  # Remplacé is_librarian par user_type
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
    
class UserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'user_type', 'phone_number', 'student_id', 'department', 'academic_level']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-control-modern',
                'placeholder': 'Prénom',
                'autocomplete': 'given-name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-control-modern',
                'placeholder': 'Nom de famille',
                'autocomplete': 'family-name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-modern',
                'placeholder': 'adresse@email.com',
                'autocomplete': 'email'
            }),
            'user_type': forms.Select(attrs={
                'class': 'form-select form-select-modern',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control form-control-modern',
                'placeholder': '+237 6XX XXX XXX',
                'autocomplete': 'tel'
            }),
            'student_id': forms.TextInput(attrs={
                'class': 'form-control form-control-modern',
                'placeholder': 'Matricule étudiant',
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control form-control-modern',
                'placeholder': 'Département/Filière',
            }),
            'academic_level': forms.Select(attrs={
                'class': 'form-select form-select-modern',
            }),
        }
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Adresse email',
            'user_type': 'Type d\'utilisateur',
            'phone_number': 'Numéro de téléphone',
            'student_id': 'Matricule étudiant',
            'department': 'Département',
            'academic_level': 'Niveau académique',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limiter les choix pour les utilisateurs standards
        self.fields['user_type'].choices = [
            ('', 'Sélectionnez un type'),
            ('STUDENT', 'Étudiant'),
            ('PROFESSOR', 'Professeur'),
        ]
        
        # Rendre certains champs obligatoires
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        
        # Ajouter des classes d'erreur pour la validation côté client
        for field_name, field in self.fields.items():
            if field.required:
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' required-field'
                else:
                    field.widget.attrs['class'] = 'required-field'
        
        # Gérer le champ matricule selon le type d'utilisateur
        if 'user_type' in self.data:
            if self.data['user_type'] != 'STUDENT':
                self.fields['student_id'].required = False
                self.fields['student_id'].widget = forms.HiddenInput()
            else:
                self.fields['student_id'].required = True
        elif self.instance.pk and self.instance.user_type != 'STUDENT':
            self.fields['student_id'].required = False
            self.fields['student_id'].widget = forms.HiddenInput()
        else:
            self.fields['student_id'].required = True

        # Gérer le champ niveau académique selon le type d'utilisateur
        if 'user_type' in self.data:
            if self.data['user_type'] != 'STUDENT':
                self.fields['academic_level'].required = False
                self.fields['academic_level'].widget = forms.HiddenInput()
            else:
                self.fields['academic_level'].required = True
                self.fields['academic_level'].choices = CustomUser.ACADEMIC_LEVELS
        elif self.instance.pk and self.instance.user_type != 'STUDENT':
            self.fields['academic_level'].required = False
            self.fields['academic_level'].widget = forms.HiddenInput()
        else:
            self.fields['academic_level'].required = True
            self.fields['academic_level'].choices = CustomUser.ACADEMIC_LEVELS

    def clean_student_id(self):
        user_type = self.cleaned_data.get('user_type')
        student_id = self.cleaned_data.get('student_id')
        
        if user_type == 'STUDENT' and not student_id:
            raise forms.ValidationError("Un matricule est requis pour les étudiants")
        return student_id

    def clean_academic_level(self):
        user_type = self.cleaned_data.get('user_type')
        academic_level = self.cleaned_data.get('academic_level')
        
        if user_type == 'STUDENT' and not academic_level:
            raise forms.ValidationError("Un niveau académique est requis pour les étudiants")
        return academic_level

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée")
        return email
    
User = get_user_model()

class CustomPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label="Ancien mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    new_password2 = forms.CharField(
        label="Confirmation",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("L'ancien mot de passe est incorrect.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("Les nouveaux mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.first_login = False
        self.user.save()
        return self.user
   
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })

class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'id': field.label.lower().replace(' ', '_')
            })

    old_password = forms.CharField(
        label="Ancien mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Confirmer le nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )