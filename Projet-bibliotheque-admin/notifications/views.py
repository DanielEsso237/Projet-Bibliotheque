from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from loans.models import Loan
from books.models import Book
from users.models import CustomUser
from django.utils import timezone
from datetime import timedelta
from .models import Notification, DeletedNotification
from django.db.models import Q
import hashlib
import logging

logger = logging.getLogger(__name__)

@login_required
def notifications(request):
    if not request.user.is_librarian:
        messages.error(request, "Seuls les bibliothécaires peuvent accéder à cette page.")
        return redirect('login')
    
    today = timezone.now().date()
    notifications = []

    # Nettoyage automatique des notifications obsolètes
    # 1. Retards résolus (prêts retournés)
    resolved_loans = Loan.objects.filter(is_returned=True)
    for loan in resolved_loans:
        deleted = Notification.objects.filter(
            Q(user=request.user) &
            Q(type__in=['warning', 'danger']) &
            Q(message__contains=loan.book.title) &
            Q(message__contains=loan.user.username)
        ).delete()
        if deleted[0] > 0:
            logger.info(f"Supprimé {deleted[0]} notifications pour prêt retourné: livre {loan.book.title}, utilisateur {loan.user.username}")
        # Supprimer les DeletedNotification associées
        DeletedNotification.objects.filter(
            Q(user=request.user) &
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

    # 2. Stocks réapprovisionnés (> 5)
    restocked_books = Book.objects.filter(is_physical=True, is_available=True, quantity__gt=5)
    for book in restocked_books:
        deleted = Notification.objects.filter(
            user=request.user,
            type='info',
            message__contains=book.title
        ).delete()
        if deleted[0] > 0:
            logger.info(f"Supprimé {deleted[0]} notifications pour stock réapprovisionné: livre {book.title}")
        # Supprimer les DeletedNotification associées
        DeletedNotification.objects.filter(
            user=request.user,
            type='info',
            unique_identifier=hashlib.sha256(
                f"Il reste {book.quantity} unité(s) de '{book.title}' dans la bibliothèque.".encode('utf-8')
            ).hexdigest()
        ).delete()

    # Notifications pour les retours proches
    overdue_loans = Loan.objects.filter(
        is_returned=False,
        due_date__gte=timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time())),
        due_date__lte=timezone.make_aware(timezone.datetime.combine(today + timedelta(days=7), timezone.datetime.max.time()))
    ).select_related('user', 'book')

    for loan in overdue_loans:
        try:
            user = loan.user
            book = loan.book
            due_date_as_date = loan.due_date.date()
            message = f"Retour proche pour '{book.title}' emprunté par {user.username} (échéance: {due_date_as_date})."
            unique_identifier = hashlib.sha256(message.encode('utf-8')).hexdigest()
            if not (Notification.objects.filter(user=request.user, unique_identifier=unique_identifier, type='warning').exists() or
                    DeletedNotification.objects.filter(user=request.user, unique_identifier=unique_identifier, type='warning').exists()):
                notification = Notification.objects.create(
                    user=request.user,
                    message=message,
                    type='warning',
                    unique_identifier=unique_identifier
                )
                logger.info(f"Notification créée: ID {notification.id}, message: {message}")
                notifications.append(notification)
            else:
                if Notification.objects.filter(user=request.user, unique_identifier=unique_identifier, type='warning').exists():
                    notification = Notification.objects.get(user=request.user, unique_identifier=unique_identifier, type='warning')
                    notifications.append(notification)
        except (CustomUser.DoesNotExist, Book.DoesNotExist):
            logger.error(f"Utilisateur ou livre introuvable pour le prêt ID {loan.id}.")

    # Notifications pour les retards
    late_loans = Loan.objects.filter(
        is_returned=False,
        due_date__lt=timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    ).select_related('user', 'book')

    for loan in late_loans:
        try:
            user = loan.user
            book = loan.book
            due_date_as_date = loan.due_date.date()
            message = f"'{book.title}' de {user.username} est en retard (échéance: {due_date_as_date})."
            unique_identifier = hashlib.sha256(message.encode('utf-8')).hexdigest()
            if not (Notification.objects.filter(user=request.user, unique_identifier=unique_identifier, type='danger').exists() or
                    DeletedNotification.objects.filter(user=request.user, unique_identifier=unique_identifier, type='danger').exists()):
                notification = Notification.objects.create(
                    user=request.user,
                    message=message,
                    type='danger',
                    unique_identifier=unique_identifier
                )
                logger.info(f"Notification créée: ID {notification.id}, message: {message}")
                notifications.append(notification)
            else:
                if Notification.objects.filter(user=request.user, unique_identifier=unique_identifier, type='danger').exists():
                    notification = Notification.objects.get(user=request.user, unique_identifier=unique_identifier, type='danger')
                    notifications.append(notification)
        except (CustomUser.DoesNotExist, Book.DoesNotExist):
            logger.error(f"Utilisateur ou livre introuvable pour le prêt ID {loan.id}.")

    # Notifications pour les stocks faibles
    low_stock_books = Book.objects.filter(is_physical=True, is_available=True, quantity__lte=5)
    for book in low_stock_books:
        try:
            message = f"Il reste {book.quantity} unité(s) de '{book.title}' dans la bibliothèque."
            unique_identifier = hashlib.sha256(message.encode('utf-8')).hexdigest()
            if not (Notification.objects.filter(user=request.user, unique_identifier=unique_identifier, type='info').exists() or
                    DeletedNotification.objects.filter(user=request.user, unique_identifier=unique_identifier, type='info').exists()):
                notification = Notification.objects.create(
                    user=request.user,
                    message=message,
                    type='info',
                    unique_identifier=unique_identifier
                )
                logger.info(f"Notification créée: ID {notification.id}, message: {message}")
                notifications.append(notification)
            else:
                if Notification.objects.filter(user=request.user, unique_identifier=unique_identifier, type='info').exists():
                    notification = Notification.objects.get(user=request.user, unique_identifier=unique_identifier, type='info')
                    notifications.append(notification)
        except Exception as e:
            logger.error(f"Erreur pour le livre ID {book.id}: {str(e)}")

    logger.info(f"Total des notifications affichées: {len(notifications)}")
    return render(request, 'notifications/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    logger.info(f"Tentative de marquage comme lu pour la notification ID {notification_id} par l'utilisateur {request.user.username}")
    if not request.user.is_librarian:
        logger.warning(f"Utilisateur non autorisé: {request.user.username}")
        return JsonResponse({'status': 'error', 'message': 'Utilisateur non autorisé'}, status=403)
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        logger.info(f"Notification marquée comme lue: ID {notification_id}")
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        logger.error(f"Notification ID {notification_id} introuvable")
        return JsonResponse({'status': 'error', 'message': 'Notification non trouvée'}, status=404)
    except Exception as e:
        logger.error(f"Erreur pour la notification ID {notification_id}: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def mark_all_notifications_as_read(request):
    logger.info(f"Tentative de marquage de toutes les notifications comme lues par l'utilisateur {request.user.username}")
    if not request.user.is_librarian:
        logger.warning(f"Utilisateur non autorisé: {request.user.username}")
        return JsonResponse({'status': 'error', 'message': 'Utilisateur non autorisé'}, status=403)
    if request.method == 'POST':
        try:
            notifications = Notification.objects.filter(user=request.user, is_read=False)
            count = notifications.update(is_read=True)
            logger.info(f"{count} notifications marquées comme lues")
            return JsonResponse({'status': 'success', 'count': count})
        except Exception as e:
            logger.error(f"Erreur: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)

@login_required
def delete_notification(request, notification_id):
    logger.info(f"Tentative de suppression de la notification ID {notification_id} par l'utilisateur {request.user.username}")
    if not request.user.is_librarian:
        logger.warning(f"Utilisateur non autorisé: {request.user.username}")
        return JsonResponse({'status': 'error', 'message': 'Utilisateur non autorisé'}, status=403)
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        DeletedNotification.objects.create(
            user=notification.user,
            unique_identifier=notification.unique_identifier,
            type=notification.type
        )
        notification.delete()
        logger.info(f"Notification supprimée: ID {notification_id}, unique_identifier: {notification.unique_identifier}")
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        logger.error(f"Notification ID {notification_id} introuvable")
        return JsonResponse({'status': 'error', 'message': 'Notification non trouvée'}, status=404)
    except Exception as e:
        logger.error(f"Erreur pour la notification ID {notification_id}: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def delete_all_notifications(request):
    logger.info(f"Tentative de suppression de toutes les notifications par l'utilisateur {request.user.username}")
    if not request.user.is_librarian:
        logger.warning(f"Utilisateur non autorisé: {request.user.username}")
        return JsonResponse({'status': 'error', 'message': 'Utilisateur non autorisé'}, status=403)
    if request.method == 'POST':
        try:
            notifications = Notification.objects.filter(user=request.user)
            for notification in notifications:
                DeletedNotification.objects.create(
                    user=notification.user,
                    unique_identifier=notification.unique_identifier,
                    type=notification.type
                )
            count = notifications.count()
            notifications.delete()
            logger.info(f"{count} notifications supprimées")
            return JsonResponse({'status': 'success', 'count': count})
        except Exception as e:
            logger.error(f"Erreur: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)

@login_required
def notification_count_api(request):
    if not request.user.is_librarian:
        return JsonResponse({'total': 0})
    
    total = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).count()
    logger.info(f"Notification count: total={total}")
    return JsonResponse({'total': total})