from notifications.models import Notification

def notification_count(request):
    if not request.user.is_authenticated or not request.user.is_librarian:
        return {'notification_counts': {'total': 0}}
    
    total_notifications = Notification.objects.filter(
        user=request.user, 
        is_read=False, 
        is_deleted=False
    ).count()
    return {
        'notification_counts': {
            'total': total_notifications
        }
    }