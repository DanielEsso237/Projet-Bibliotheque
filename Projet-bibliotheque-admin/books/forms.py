from django import forms
from .models import Book, Document

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'isbn', 'publication_date', 'category',
            'ebook_file', 'cover_image'
        ]
        labels = {
            'title': 'Titre',
            'author': 'Auteur',
            'isbn': 'ISBN',
            'publication_date': 'Date de publication',
            'category': 'Catégorie',
            'ebook_file': 'Fichier PDF',
            'cover_image': 'Image de couverture',
        }
        help_texts = {
            'isbn': '13 caractères (facultatif)',
            'ebook_file': 'Uniquement fichiers PDF',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'ebook_file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ebook_file'].required = False  # Non requis pour l'édition

    def clean(self):
        cleaned_data = super().clean()
        ebook_file = cleaned_data.get('ebook_file')

        if ebook_file and not ebook_file.name.endswith('.pdf'):
            self.add_error('ebook_file', "Seuls les fichiers PDF sont acceptés.")

        return cleaned_data

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'author', 'file', 'cover_image', 'is_available']
        labels = {
            'title': 'Titre',
            'author': 'Auteur',
            'file': 'Fichier PDF',
            'cover_image': 'Image de couverture',
            'is_available': 'Disponible ?',
        }
        help_texts = {
            'file': 'Uniquement fichiers PDF (facultatif)',
            'author': 'Facultatif pour les documents académiques',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')

        if file and not file.name.endswith('.pdf'):
            self.add_error('file', "Seuls les fichiers PDF sont acceptés.")

        return cleaned_data  