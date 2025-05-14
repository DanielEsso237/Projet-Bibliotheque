from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)  # Titre du livre
    author = models.CharField(max_length=100)  # Nom de l'auteur
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)  # ISBN, unique mais facultatif
    publication_date = models.DateField(blank=True, null=True)  # Date de publication, facultative
    quantity = models.PositiveIntegerField(default=0, blank=True, null=True)  # Ajouter blank=True et null=True  # Quantité d'exemplaires, ne peut pas être négative
    category = models.CharField(max_length=50, blank=True)  # Catégorie (ex. roman, science, etc.)
    is_physical = models.BooleanField(default=True)  # True pour physique, False pour virtuel
    ebook_file = models.FileField(upload_to='ebooks/', blank=True, null=True)  # Fichier PDF pour livres numériques
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)  # Photo de couverture
    is_available = models.BooleanField(default=True)  # Disponible pour l'emprunt
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de dernière modification
    is_borrowed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        ordering = ['title']
        verbose_name = "Book"
        verbose_name_plural = "Books"