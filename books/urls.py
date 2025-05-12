# books/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # exemple de route
    path('', views.librarian_dashboard, name='books-index'),
    path('add/', views.add_book, name='add_book'),
    path('', views.librarian_dashboard, name='librarian_dashboard'),
    path('current-loans/', views.current_loans, name='current_loans'),
]
