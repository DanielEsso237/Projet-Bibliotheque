from django.db import models
from users.models import CustomUser
from books.models import Book
from django.utils import timezone

class Loan(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='loans')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    loan_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField()
    is_returned = models.BooleanField(default=False)
    fine = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Amende en euros

    def __str__(self):
        return f"{self.book.title} emprunté par {self.user.username} (Due: {self.due_date})"

    class Meta:
        ordering = ['-loan_date']