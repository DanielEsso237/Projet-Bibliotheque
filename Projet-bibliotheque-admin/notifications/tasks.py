from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from notifications.models import DeletedNotification
from loans.models import Loan
from books.models import Book
from settings_app.models import SystemSettings
from django.db.models import Q
import hashlib
import logging

logger = logging.getLogger(__name__)

@shared_task
def clean_deleted_notifications():
    try:
        # Récupérer le seuil dynamique
        settings = SystemSettings.objects.first()
        threshold_days = settings.notification_cleanup_days if settings else 30

        # Supprimer les entrées de plus de threshold_days jours
        threshold_date = timezone.now() - timedelta(days=threshold_days)
        old_notifications = DeletedNotification.objects.filter(deleted_at__lt=threshold_date)
        old_count = old_notifications.count()
        old_notifications.delete()
        if old_count > 0:
            logger.info(f"Supprimé {old_count} entrées de DeletedNotification de plus de {threshold_days} jours.")

        # Supprimer les entrées liées à des prêts retournés
        resolved_loans = Loan.objects.filter(is_returned=True)
        for loan in resolved_loans:
            deleted = DeletedNotification.objects.filter(
                Q(user=loan.user) &
                Q(type__in=['warning', 'danger']) &
                Q(unique_identifier__in=[
                    hashlib.sha256(
                        f"Retour proche pour '{loan.book.title}' emprunté par {loan.user.username} (échéance: {loan.due_date.date()}).".encode('utf-8')
                    ).hexdigest(),
                    hashlib.sha256(
                        f"'{loan.book.title}' de {loan.user.username} est en retard (échéance: {loan.due_date.date()}).".encode('utf-8')
                    ).hexdigest()
                ])
            ).delete()
            if deleted[0] > 0:
                logger.info(f"Supprimé {deleted[0]} entrées de DeletedNotification pour prêt retourné: livre {loan.book.title}, utilisateur {loan.user.username}")

        # Supprimer les entrées liées à des livres réapprovisionnés
        restocked_books = Book.objects.filter(is_physical=True, is_available=True, quantity__gt=5)
        for book in restocked_books:
            deleted = DeletedNotification.objects.filter(
                user__is_librarian=True,
                type='info',
                unique_identifier=hashlib.sha256(
                    f"Il reste {book.quantity} unité(s) de '{book.title}' dans la bibliothèque.".encode('utf-8')
                ).hexdigest()
            ).delete()
            if deleted[0] > 0:
                logger.info(f"Supprimé {deleted[0]} entrées de DeletedNotification pour stock réapprovisionné: livre {book.title}")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de DeletedNotification: {str(e)}")