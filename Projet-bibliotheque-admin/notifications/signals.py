from django.db.models.signals import post_save
from django.dispatch import receiver
from loans.models import Loan
from notifications.models import Notification, DeletedNotification
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Loan)
def update_loan_notifications(sender, instance, created, **kwargs):
    if instance.is_returned:
        try:
            deleted = Notification.objects.filter(
                Q(user=instance.user) &
                Q(type__in=['warning', 'danger']) &
                Q(message__contains=instance.book.title) &
                Q(message__contains=instance.user.username)
            ).delete()
            if deleted[0] > 0:
                logger.info(f"Supprimé {deleted[0]} notifications pour prêt retourné: livre {instance.book.title}, utilisateur {instance.user.username}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression des notifications pour le prêt ID {instance.id}: {str(e)}")