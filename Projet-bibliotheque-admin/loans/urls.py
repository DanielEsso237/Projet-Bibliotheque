from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('', views.loan_list, name='loan_list'),
    path('return/<int:loan_id>/', views.return_book, name='return_book'),
    path('create/', views.create_loan, name='create_loan'),
    path('api/search/', views.search_loans_api, name='search_loans_api'),
    path('late/', views.late_books, name='late_books'),
    path('api/search-users/', views.search_users_api, name='search_users_api'),
    path('api/search-books/', views.search_books_api, name='search_books_api'),
]