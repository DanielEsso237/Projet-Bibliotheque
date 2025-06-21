from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from books.models import Book, Document
from users.models import CustomUser
from notifications.models import Notification, DeletedNotification
import hashlib

@receiver(post_save, sender=Book)
def notify_book_added_or_updated(sender, instance, created, **kwargs):
    librarians = CustomUser.objects.filter(user_type='LIBRARIAN')
    message = f"Un nouvel e-book '{instance.title}' a été ajouté." if created else f"L’e-book '{instance.title}' a été modifié."
    type_notification = 'info-new' if created else 'info-update'
    
    for librarian in librarians:
        unique_identifier = hashlib.sha256(message.encode('utf-8')).hexdigest()
        if not (Notification.objects.filter(user=librarian, unique_identifier=unique_identifier, type=type_notification).exists() or
                DeletedNotification.objects.filter(user=librarian, unique_identifier=unique_identifier, type=type_notification).exists()):
            Notification.objects.create(
                user=librarian,
                message=message,
                type=type_notification,
                unique_identifier=unique_identifier
            )

@receiver(post_delete, sender=Book)
def notify_book_deleted(sender, instance, **kwargs):
    librarians = CustomUser.objects.filter(user_type='LIBRARIAN')
    message = f"L’e-book '{instance.title}' a été supprimé."
    type_notification = 'warning-delete'
    
    for librarian in librarians:
        unique_identifier = hashlib.sha256(message.encode('utf-8')).hexdigest()
        if not (Notification.objects.filter(user=librarian, unique_identifier=unique_identifier, type=type_notification).exists() or
                DeletedNotification.objects.filter(user=librarian, unique_identifier=unique_identifier, type=type_notification).exists()):
            Notification.objects.create(
                user=librarian,
                message=message,
                type=type_notification,
                unique_identifier=unique_identifier
            )

@receiver(post_save, sender=Document)
def notify_document_added_or_updated(sender, instance, created, **kwargs):
    librarians = CustomUser.objects.filter(user_type='LIBRARIAN')
    message = f"Un nouveau document '{instance.title}' ({instance.get_document_type_display()}) a été ajouté." if created else f"Le document '{instance.title}' ({instance.get_document_type_display()}) a été modifié."
    type_notification = 'info-new' if created else 'info-update'
    
    for librarian in librarians:
        unique_identifier = hashlib.sha256(message.encode('utf-8')).hexdigest()
        if not (Notification.objects.filter(user=librarian, unique_identifier=unique_identifier, type=type_notification).exists() or
                DeletedNotification.objects.filter(user=librarian, unique_identifier=unique_identifier, type=type_notification).exists()):
            Notification.objects.create(
                user=librarian,
                message=message,
                type=type_notification,
                unique_identifier=unique_identifier
            )

    # Notifier les utilisateurs correspondant au niveau académique
    if created:
        users = CustomUser.objects.filter(academic_level=instance.academic_level)
        message_user = f"Un nouveau document '{instance.title}' ({instance.get_document_type_display()}) est disponible pour {instance.get_academic_level_display()}."
        for user in users:
            unique_identifier = hashlib.sha256(message_user.encode('utf-8')).hexdigest()
            if not (Notification.objects.filter(user=user, unique_identifier=unique_identifier, type='info-new').exists() or
                    DeletedNotification.objects.filter(user=user, unique_identifier=unique_identifier, type='info-new').exists()):
                Notification.objects.create(
                    user=user,
                    message=message_user,
                    type='info-new',
                    unique_identifier=unique_identifier
                )

@receiver(post_delete, sender=Document)
def notify_document_deleted(sender, instance, **kwargs):
    librarians = CustomUser.objects.filter(user_type='LIBRARIAN')
    message = f"Le document '{instance.title}' ({instance.get_document_type_display()}) a été supprimé."
    type_notification = 'warning-delete'
    
    for librarian in librarians:
        unique_identifier = hashlib.sha256(message.encode('utf-8')).hexdigest()
        if not (Notification.objects.filter(user=librarian, unique_identifier=unique_identifier, type=type_notification).exists() or
                DeletedNotification.objects.filter(user=librarian, unique_identifier=unique_identifier, type=type_notification).exists()):
            Notification.objects.create(
                user=librarian,
                message=message,
                type=type_notification,
                unique_identifier=unique_identifier
            )

@receiver(post_save, sender=CustomUser)
def notify_user_added(sender, instance, created, **kwargs):
    if created and instance.user_type != 'LIBRARIAN':
        librarians = CustomUser.objects.filter(user_type='LIBRARIAN')
        message = f"Un nouvel utilisateur '{instance.username}' s’est inscrit."
        type_notification = 'info-user'
        
        for librarian in librarians:
            unique_identifier = hashlib.sha256(message.encode('utf-8')).hexdigest()
            if not (Notification.objects.filter(user=librarian, unique_identifier=unique_identifier, type=type_notification).exists() or
                    DeletedNotification.objects.filter(user=librarian, unique_identifier=unique_identifier, type=type_notification).exists()):
                Notification.objects.create(
                    user=librarian,
                    message=message,
                    type=type_notification,
                    unique_identifier=unique_identifier
                )