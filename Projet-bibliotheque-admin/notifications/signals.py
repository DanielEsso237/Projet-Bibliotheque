from django.db.models.signals import post_save
from django.dispatch import receiver
from loans.models import Loan
from books.models import Book
from notifications.models import Notification
import hashlib

@receiver(post_save, sender=Loan)
def update_loan_notifications(sender, instance, **kwargs):
    if instance.is_returned:
        message = f"Retour proche pour '{instance.book.title}' emprunté par {instance.user.username} (échéance: {instance.due_date.date()})."
        unique_identifier = hashlib.sha256(message.encode('utf-8')).hexdigest()
        Notification.objects.filter(
            user__is_librarian=True,
            unique_identifier=unique_identifier,
            type='warning'
        ).update(is_deleted=True)
        message = f"'{instance.book.title}' de {instance.user.username} est en retard (échéance: {instance.due_date.date()})."
        unique_identifier = hashlib.sha256(message.encode('utf-8')).hexdigest()
        Notification.objects.filter(
            user__is_librarian=True,
            unique_identifier=unique_identifier,
            type='danger'
        ).update(is_deleted=True)

@receiver(post_save, sender=Book)
def update_book_notifications(sender, instance, **kwargs):
    if instance.quantity > 5:
        message = f"Il reste {instance.quantity} unité(s) de '{instance.title}' dans la bibliothèque."
        unique_identifier = hashlib.sha256(message.encode('utf-8')).hexdigest()
        Notification.objects.filter(
            user__is_librarian=True,
            unique_identifier=unique_identifier,
            type='info'
        ).update(is_deleted=True)