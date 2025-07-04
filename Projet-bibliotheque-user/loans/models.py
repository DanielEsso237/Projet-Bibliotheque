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
        managed = True
        db_table = 'loans_history'
        ordering = ['-loan_date']
        

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Loan)
def update_history(sender, instance, **kwargs):
    if instance.is_returned and not History.objects.filter(user=instance.user, book=instance.book).exists():
        History.objects.create(
            user=instance.user,
            book=instance.book,
            genre=instance.book.category or '',
            loan_date=instance.loan_date,
            is_physical=instance.is_physical
        )