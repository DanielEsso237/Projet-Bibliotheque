from django import forms
from .models import Book, Document

class BookForm(forms.ModelForm):
    # Redéfinir category comme ChoiceField dans le formulaire
    category = forms.ChoiceField(
        choices=[
            ('', '---------'),
            ('informatique', 'Informatique'),
            ('physique', 'Physique'),
            ('chimie', 'Chimie'),
            ('mathematiques', 'Mathématiques'),
            ('sciences', 'Sciences'),
            ('biotechnologie', 'Biotechnologie'),
            ('agriculture', 'Agriculture'),
            ('elevage', 'Élevage'),
            ('technologie', 'Technologie'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    custom_category = forms.CharField(
        max_length=50,
        required=False,
        label="Catégorie personnalisée",
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'display: none;'})
    )

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
            'category': 'Choisissez une catégorie ou entrez une nouvelle si nécessaire',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ebook_file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ebook_file'].required = False  # Non requis pour l'édition

    def clean(self):
        cleaned_data = super().clean()
        ebook_file = cleaned_data.get('ebook_file')
        category = cleaned_data.get('category')
        custom_category = cleaned_data.get('custom_category')

        if ebook_file and not ebook_file.name.endswith('.pdf'):
            self.add_error('ebook_file', "Seuls les fichiers PDF sont acceptés.")

        # Si custom_category est rempli, utiliser cette valeur
        if custom_category:
            cleaned_data['category'] = custom_category
        elif not category and not custom_category:
            self.add_error('category', "Veuillez entrer une catégorie.")

        # Supprimer custom_category des données nettoyées
        if 'custom_category' in cleaned_data:
            del cleaned_data['custom_category']

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