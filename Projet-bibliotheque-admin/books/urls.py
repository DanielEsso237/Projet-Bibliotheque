# books/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # exemple de route
    path('', views.librarian_dashboard, name='books-index'),
    path('add/', views.add_book, name='add_book'),
    path('', views.librarian_dashboard, name='librarian_dashboard'),
    path('delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('api/book/<int:book_id>/', views.book_api, name='book_api'),
    path('api/search/', views.search_books_api, name='search_books_api'),
] 
