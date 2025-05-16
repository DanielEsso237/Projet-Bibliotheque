from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.loan_list, name='loan_list'),
    path('return/<int:loan_id>/', views.return_book, name='return_book'),
    path('create/', views.create_loan, name='create_loan'),  # Nouvelle URL
    path('api/search/', views.search_loans_api, name='search_loans_api'),
]