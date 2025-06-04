from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    category = models.CharField(max_length=50, blank=True)
    is_physical = models.BooleanField(default=True)
    ebook_file = models.FileField(upload_to='ebooks/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_borrowed = models.BooleanField(default=False)
    is_ebook = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        ordering = ['title']
        verbose_name = "Book"
        verbose_name_plural = "Books"

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('ebook', 'E-book'),
        ('exam', 'Épreuve'),
        ('course', 'Support de cours'),
        ('td', 'Fiche de TD'),
        ('article', 'Article'),
    ]
    ACADEMIC_LEVELS = [
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
        ('D', 'Doctorat'),
        ('N/A', 'Non applicable'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    academic_level = models.CharField(max_length=10, choices=ACADEMIC_LEVELS, default='N/A')
    file = models.FileField(upload_to='documents/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)  # Nouveau champ
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"

    class Meta:
        ordering = ['title']
        verbose_name = "Document"
        verbose_name_plural = "Documents"