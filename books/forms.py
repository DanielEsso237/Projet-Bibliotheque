from django import forms
from .models import Book

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

    def clean(self):
        cleaned_data = super().clean()
        is_physical = cleaned_data.get('is_physical')
        ebook_file = cleaned_data.get('ebook_file')

        if not is_physical and not ebook_file:
            self.add_error('ebook_file', "Un fichier PDF est requis pour les livres numériques.")
        elif ebook_file and not ebook_file.name.endswith('.pdf'):
            self.add_error('ebook_file', "Seuls les fichiers PDF sont acceptés.")

        return cleaned_data