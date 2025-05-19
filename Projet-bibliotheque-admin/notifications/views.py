from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from loans.models import Loan
from books.models import Book
from django.utils import timezone
from datetime import timedelta
from .models import Notification

@login_required
def notifications(request):
    if not request.user.is_librarian:
        messages.error(request, "Seuls les bibliothécaires peuvent accéder à cette page.")
        return redirect('login')
    
    today = timezone.now().date()
    notifications = []

    # Supprimer les notifications obsolètes
    Notification.objects.filter(user=request.user).exclude(
        message__in=Loan.objects.filter(is_returned=False).values_list('id', flat=True)
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
            due_date_as_date = loan.due_date.date()
            days_left = (due_date_as_date - today).days
            message = f"Il reste {days_left} jour(s) à {user.username} pour rendre '{loan.book.title}' (échéance: {loan.due_date})."
            notification, created = Notification.objects.update_or_create(
                user=request.user,
                message=message,
                defaults={'type': 'warning', 'is_read': False}
            )
            notifications.append(notification)
        except (CustomUser.DoesNotExist, Book.DoesNotExist):
            print(f"Utilisateur ou livre introuvable pour le prêt ID {loan.id}. Considérer la suppression de ce prêt.")

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
            days_late = (today - due_date_as_date).days
            fine_amount = days_late * 0.10
            loan.fine = fine_amount
            loan.save()
            message = f"'{book.title}' de {user.username} est en retard de {days_late} jour(s) (amende: {fine_amount:.2f} €)."
            notification, created = Notification.objects.update_or_create(
                user=request.user,
                message=message,
                defaults={'type': 'danger', 'is_read': False}
            )
            notifications.append(notification)
        except (CustomUser.DoesNotExist, Book.DoesNotExist):
            print(f"Utilisateur ou livre introuvable pour le prêt ID {loan.id}. Considérer la suppression de ce prêt.")

    # Notifications pour les stocks faibles
    low_stock_books = Book.objects.filter(is_physical=True, is_available=True, quantity__lte=5)
    for book in low_stock_books:
        message = f"Il reste {book.quantity} unité(s) de '{book.title}' dans la bibliothèque."
        notification, created = Notification.objects.update_or_create(
            user=request.user,
            message=message,
            defaults={'type': 'info', 'is_read': False}
        )
        notifications.append(notification)

    return render(request, 'notifications/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    if not request.user.is_librarian:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def notification_count_api(request):
    if not request.user.is_librarian:
        return JsonResponse({'total': 0, 'overdue': 0, 'late': 0, 'low_stock': 0})
    
    today = timezone.now().date()
    overdue = Notification.objects.filter(user=request.user, type='warning', is_read=False).count()
    late = Notification.objects.filter(user=request.user, type='danger', is_read=False).count()
    low_stock = Notification.objects.filter(user=request.user, type='info', is_read=False).count()
    total = overdue + late + low_stock
    return JsonResponse({
        'total': total,
        'overdue': overdue,
        'late': late,
        'low_stock': low_stock
    })