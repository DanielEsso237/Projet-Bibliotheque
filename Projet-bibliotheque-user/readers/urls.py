from django.urls import path
from . import views

app_name = 'readers'
urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('profile/', views.profile_view, name='profile'),
]