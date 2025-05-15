from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from loans.models import Loan
from books.models import Book
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from .models import Notification
from django.shortcuts import get_object_or_404

@login_required
def notifications(request):
    if not request.user.is_librarian:
        messages.error(request, "Seuls les bibliothécaires peuvent accéder à cette page.")
        return redirect('login')
    
    today = timezone.now().date()
    
    # Supprimer les anciennes notifications non lues
    Notification.objects.filter(user=request.user, is_read=False).delete()

    # Générer de nouvelles notifications
    overdue_loans = Loan.objects.filter(
        is_returned=False,
        due_date__gte=timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time())),
        due_date__lte=timezone.make_aware(timezone.datetime.combine(today + timedelta(days=7), timezone.datetime.max.time()))
    )
    for loan in overdue_loans:
        due_date_as_date = loan.due_date.date()
        days_left = (due_date_as_date - today).days
        Notification.objects.create(
            user=request.user,
            message=f"Il reste {days_left} jour(s) à {loan.user.username} pour rendre '{loan.book.title}' (échéance: {loan.due_date}).",
            type='warning'
        )

    late_loans = Loan.objects.filter(
        is_returned=False,
        due_date__lt=timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    )
    for loan in late_loans:
        due_date_as_date = loan.due_date.date()
        days_late = (today - due_date_as_date).days
        fine_amount = days_late * 0.10
        loan.fine = fine_amount
        loan.save()
        Notification.objects.create(
            user=request.user,
            message=f"'{loan.book.title}' de {loan.user.username} est en retard de {days_late} jour(s) (amende: {fine_amount:.2f} €).",
            type='danger'
        )

    low_stock_books = Book.objects.filter(is_physical=True, is_available=True, quantity__lte=5)
    for book in low_stock_books:
        Notification.objects.create(
            user=request.user,
            message=f"Il reste {book.quantity} unité(s) de '{book.title}' dans la bibliothèque.",
            type='info'
        )

    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    if not request.user.is_librarian:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})


@login_required
def notification_count_api(request):
    if not request.user.is_librarian:
        return JsonResponse({'total': 0, 'overdue': 0, 'late': 0, 'low_stock': 0})
    
    today = timezone.now().date()
    overdue_loans = Loan.objects.filter(
        is_returned=False,
        due_date__gte=timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time())),
        due_date__lte=timezone.make_aware(timezone.datetime.combine(today + timedelta(days=7), timezone.datetime.max.time()))
    ).count()
    late_loans = Loan.objects.filter(
        is_returned=False,
        due_date__lt=timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    ).count()
    low_stock_books = Book.objects.filter(is_physical=True, is_available=True, quantity__lte=5).count()
    total_notifications = overdue_loans + late_loans + low_stock_books
    return JsonResponse({
        'total': total_notifications,
        'overdue': overdue_loans,
        'late': late_loans,
        'low_stock': low_stock_books
    })