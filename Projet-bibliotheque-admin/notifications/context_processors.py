from loans.models import Loan
from books.models import Book
from notifications.models import Notification
from django.utils import timezone

def notification_count(request):
    if not request.user.is_authenticated or not request.user.is_librarian:
        return {'notification_counts': {'total': 0, 'overdue': 0, 'late': 0, 'low_stock': 0}}
    
    overdue = Notification.objects.filter(user=request.user, type='warning', is_read=False).count()
    late = Notification.objects.filter(user=request.user, type='danger', is_read=False).count()
    low_stock = Notification.objects.filter(user=request.user, type='info', is_read=False).count()
    total_notifications = overdue + late + low_stock
    return {
        'notification_counts': {
            'total': total_notifications,
            'overdue': overdue,
            'late': late,
            'low_stock': low_stock
        }
    }