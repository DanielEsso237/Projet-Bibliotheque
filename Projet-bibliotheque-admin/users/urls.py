from django.urls import path
from . import views

app_name = 'users'  # Ajout du namespace

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('update-user/<int:user_id>/', views.update_user, name='update_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('create/', views.create_user, name='create_user'),
    path('change-password/', views.change_password, name='change_password'),
]