from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from loans.models import Loan
from books.models import Book
from django.utils import timezone
from datetime import timedelta
from .models import Notification
import logging

logger = logging.getLogger(__name__)

@login_required
def notifications(request):
    if not request.user.is_librarian:
        messages.error(request, "Seuls les bibliothécaires peuvent accéder à cette page.")
        return redirect('login')
    
    today = timezone.now().date()
    notifications = []

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
            message = f"Retour proche pour '{book.title}' emprunté par {user.username} (échéance: {loan.due_date.date()})."
            notification, created = Notification.objects.get_or_create(
                user=request.user,
                message=message,
                type='warning'
            )
            if created:
                logger.info(f"Notification créée: ID {notification.id}, message: {message}")
            else:
                logger.info(f"Notification existante: ID {notification.id}, is_read: {notification.is_read}")
            notifications.append(notification)
        except (CustomUser.DoesNotExist, Book.DoesNotExist):
            logger.error(f"Utilisateur ou livre introuvable pour le prêt ID {loan.id}. Considérer la suppression de ce prêt.")

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
            notification, created = Notification.objects.get_or_create(
                user=request.user,
                message=message,
                type='danger'
            )
            if created:
                logger.info(f"Notification créée: ID {notification.id}, message: {message}")
            else:
                logger.info(f"Notification existante: ID {notification.id}, is_read: {notification.is_read}")
            notifications.append(notification)
        except (CustomUser.DoesNotExist, Book.DoesNotExist):
            logger.error(f"Utilisateur ou livre introuvable pour le prêt ID {loan.id}. Considérer la suppression de ce prêt.")

    # Notifications pour les stocks faibles
    low_stock_books = Book.objects.filter(is_physical=True, is_available=True, quantity__lte=5)
    for book in low_stock_books:
        message = f"Il reste {book.quantity} unité(s) de '{book.title}' dans la bibliothèque."
        notification, created = Notification.objects.get_or_create(
            user=request.user,
            message=message,
            type='info'
        )
        if created:
            logger.info(f"Notification créée: ID {notification.id}, message: {message}")
        else:
            logger.info(f"Notification existante: ID {notification.id}, is_read: {notification.is_read}")
        notifications.append(notification)

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
        logger.info(f"Notification trouvée: ID {notification_id}, message: {notification.message}, is_read: {notification.is_read}")
        notification.is_read = True
        notification.save()
        notification.refresh_from_db()
        logger.info(f"Après sauvegarde: Notification ID {notification_id}, is_read: {notification.is_read}")
        if not notification.is_read:
            logger.error(f"Échec de la mise à jour de is_read pour la notification ID {notification_id}")
            return JsonResponse({'status': 'error', 'message': 'Échec de la mise à jour de la notification'}, status=500)
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        logger.error(f"Notification ID {notification_id} introuvable pour l'utilisateur {request.user.username}")
        return JsonResponse({'status': 'error', 'message': 'Notification non trouvée'}, status=404)
    except Exception as e:
        logger.error(f"Erreur lors du marquage de la notification ID {notification_id}: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def notification_count_api(request):
    if not request.user.is_librarian:
        return JsonResponse({'total': 0, 'overdue': 0, 'late': 0, 'low_stock': 0})
    
    today = timezone.now().date()
    overdue = Notification.objects.filter(user=request.user, type='warning', is_read=False).count()
    late = Notification.objects.filter(user=request.user, type='danger', is_read=False).count()
    low_stock = Notification.objects.filter(user=request.user, type='info', is_read=False).count()
    total = overdue + late + low_stock
    logger.info(f"Notification count: total={total}, overdue={overdue}, late={late}, low_stock={low_stock}")
    return JsonResponse({
        'total': total,
        'overdue': overdue,
        'late': late,
        'low_stock': low_stock
    })