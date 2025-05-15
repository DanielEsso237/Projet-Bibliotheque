from loans.models import Loan
from books.models import Book
from django.utils import timezone
from datetime import timedelta

def notification_count(request):
    if not request.user.is_authenticated or not request.user.is_librarian:
        return {'notification_counts': {'total': 0, 'overdue': 0, 'late': 0, 'low_stock': 0}}
    
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
    return {
        'notification_counts': {
            'total': total_notifications,
            'overdue': overdue_loans,
            'late': late_loans,
            'low_stock': low_stock_books
        }
    }