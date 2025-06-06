from django.db import models
from users.models import CustomUser
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, blank=True, null=True)
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

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        managed = True
        db_table = 'books_book'
        
        
class UserFavorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        unique_together = ('user', 'book')  # Un utilisateur ne peut ajouter un livre en favori qu'une fois
        db_table = 'books_user_favorite'

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"