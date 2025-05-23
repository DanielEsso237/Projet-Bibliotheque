from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'clean-deleted-notifications-every-day': {
        'task': 'notifications.tasks.clean_deleted_notifications',
        'schedule': crontab(hour=0, minute=0),
    },
}