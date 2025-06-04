from django import forms
from .models import Book, Document

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'isbn', 'publication_date', 'quantity',
            'category', 'is_physical', 'ebook_file', 'cover_image', 'is_available'
        ]
        labels = {
            'title': 'Titre',
            'author': 'Auteur',
            'isbn': 'ISBN',
            'publication_date': 'Date de publication',
            'quantity': 'Quantité',
            'category': 'Catégorie',
            'is_physical': 'Livre physique ?',
            'ebook_file': 'Fichier PDF',
            'cover_image': 'Image de couverture',
            'is_available': 'Disponible ?',
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
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'is_physical': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ebook_file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].required = False
        self.fields['ebook_file'].required = False

    def clean(self):
        cleaned_data = super().clean()
        is_physical = cleaned_data.get('is_physical')
        ebook_file = cleaned_data.get('ebook_file')
        quantity = cleaned_data.get('quantity')

        if not is_physical:
            if not ebook_file:
                self.add_error('ebook_file', "Un fichier PDF est requis pour les livres numériques.")
            elif ebook_file and not ebook_file.name.endswith('.pdf'):
                self.add_error('ebook_file', "Seuls les fichiers PDF sont acceptés.")
        else:
            if quantity is None or quantity <= 0:
                self.add_error('quantity', "La quantité doit être supérieure à 0 pour un livre physique.")

        return cleaned_data

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'author', 'document_type', 'academic_level', 'file', 'is_available']
        labels = {
            'title': 'Titre',
            'author': 'Auteur',
            'document_type': 'Type de document',
            'academic_level': 'Niveau académique',
            'file': 'Fichier PDF',
            'is_available': 'Disponible ?',
        }
        help_texts = {
            'file': 'Uniquement fichiers PDF',
            'author': 'Facultatif pour les documents académiques',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'academic_level': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        document_type = cleaned_data.get('document_type')
        academic_level = cleaned_data.get('academic_level')
        file = cleaned_data.get('file')

        if not file:
            self.add_error('file', "Un fichier PDF est requis.")
        elif not file.name.endswith('.pdf'):
            self.add_error('file', "Seuls les fichiers PDF sont acceptés.")

        if document_type != 'ebook' and academic_level == 'N/A':
            self.add_error('academic_level', "Un niveau académique est requis pour ce type de document.")

        return cleaned_data