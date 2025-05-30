from django.db import models
from django.utils import timezone
from users.models import CustomUser
from books.models import Book

class Loan(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='loans')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    loan_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    fine = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_physical = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    class Meta:
        managed = False  # Table gérée par l'admin
        db_table = 'loans_loan'  # Nom de la table dans librairy_db
        ordering = ['-loan_date']
        
class History(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='history')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='history')
    genre = models.CharField(max_length=50)
    loan_date = models.DateTimeField()
    is_physical = models.BooleanField()

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.genre})"

    class Meta:
        managed = False
        db_table = 'loans_history'
        ordering = ['-loan_date']