from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification, DeletedNotification
import logging

logger = logging.getLogger(__name__)

@login_required
def notifications(request):
    if not request.user.user_type == 'LIBRARIAN':
        messages.error(request, "Seuls les bibliothécaires peuvent accéder à cette page.")
        return redirect('login')
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    logger.info(f"Total des notifications affichées: {notifications.count()}")
    return render(request, 'notifications/notifications.html', {'notifications': notifications})

@login_required
def user_notifications(request):
    if request.user.user_type == 'LIBRARIAN':
        messages.error(request, "Cette page est réservée aux utilisateurs non-bibliothécaires.")
        return redirect('notifications')
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    logger.info(f"Total des notifications utilisateur affichées: {notifications.count()}")
    return render(request, 'notifications/user_notifications.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    logger.info(f"Tentative de marquage comme lu pour la notification ID {notification_id} par l'utilisateur {request.user.username}")
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
    total = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).count()
    logger.info(f"Notification count: total={total}")
    return JsonResponse({'total': total})