from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'publication_date', 'quantity', 'category', 'is_physical', 'file_url', 'cover_image', 'is_available']