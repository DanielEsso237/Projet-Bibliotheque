from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications, name='notifications'),
    path('mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('mark-all-as-read/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    path('count/', views.notification_count_api, name='notification_count_api'),
    path('delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('delete-all/', views.delete_all_notifications, name='delete_all_notifications'),
]