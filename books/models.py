from django.db import models
from django.core.validators import FileExtensionValidator

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    category = models.CharField(max_length=50, blank=True)
    ebook_file = models.FileField(upload_to='ebooks/', validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    @property
    def item_type(self):
        return 'book'

    class Meta:
        ordering = ['title']
        verbose_name = "E-book"
        verbose_name_plural = "E-books"

class Document(models.Model):
    DOCUMENT_TYPES = [('exam', 'Épreuve'), ('course', 'Support de cours'), ('td', 'Fiche de TD'), ('article', 'Article')]
    ACADEMIC_LEVELS = [('L1', 'Licence 1'), ('L2', 'Licence 2'), ('L3', 'Licence 3'), ('M1', 'Master 1'), ('M2', 'Master 2'), ('D', 'Doctorat')]
    DEPARTMENTS = [('Chimie appliquée', 'Chimie appliquée'), ('Géosciences', 'Géosciences'), ('Physique appliquée', 'Physique appliquée'), ('ROSE', 'ROSE'), ('SBAA', 'SBAA'), ('SBM', 'SBM'), ('TBM', 'TBM'), ('TIC', 'TIC')]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    academic_level = models.CharField(max_length=10, choices=ACADEMIC_LEVELS)
    department = models.CharField(max_length=50, choices=DEPARTMENTS, blank=True, null=True)
    file = models.FileField(upload_to='documents/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"

    @property
    def item_type(self):
        return 'document'

    class Meta:
        ordering = ['title']
        verbose_name = "Document"
        verbose_name_plural = "Documents"