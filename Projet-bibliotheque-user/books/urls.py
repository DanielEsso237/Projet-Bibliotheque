from django.urls import path
from . import views

app_name = 'books'
urlpatterns = [
    path('search/', views.search_view, name='search'),
    path('detail/<int:pk>/', views.book_detail_view, name='detail'),
]