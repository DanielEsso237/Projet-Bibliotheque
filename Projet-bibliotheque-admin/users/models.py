from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import random
from books.models import Book

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('LIBRARIAN', 'Bibliothécaire'),
        ('STUDENT', 'Étudiant'),
        ('PROFESSOR', 'Professeur'),
    )
    
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES, default='STUDENT')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    student_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    first_login = models.BooleanField(default=True)  # Pour forcer le changement de mot de passe

    def save(self, *args, **kwargs):
        # Génération automatique du username si c'est un nouvel utilisateur
        if not self.pk and not self.username:
            base_username = f"{slugify(self.last_name)}.{slugify(self.first_name)}"
            self.username = base_username
            
            # Vérifier l'unicité et ajouter un suffixe numérique si nécessaire
            suffix = 1
            while CustomUser.objects.filter(username=self.username).exists():
                self.username = f"{base_username}{suffix:03d}"
                suffix += 1
        
        # Si c'est un étudiant, vérifier qu'un matricule est fourni
        if self.user_type == 'STUDENT' and not self.student_id:
            raise ValueError("Un matricule est requis pour les étudiants")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    
    
class UserFavorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        unique_together = ('user', 'book')
        db_table = 'books_user_favorite'

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"