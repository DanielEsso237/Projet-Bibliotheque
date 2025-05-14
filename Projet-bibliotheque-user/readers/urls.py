from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='readers_home'),
    path('register/', views.register_view, name='readers_register'),
    path('login/', views.login_view, name='readers_login'),
    path('logout/', views.logout_view, name='readers_logout'),
]