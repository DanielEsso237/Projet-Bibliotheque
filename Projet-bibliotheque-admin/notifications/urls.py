from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications, name='notifications'),
    path('count/', views.notification_count_api, name='notification_count_api'),
    path('mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('mark-all-as-read/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
]