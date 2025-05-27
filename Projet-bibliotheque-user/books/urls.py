from django.urls import path
from . import views

app_name = 'books'
urlpatterns = [
    path('search/', views.search_view, name='search'),
    path('loans/', views.loans_view, name='loans'),
]