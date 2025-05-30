from django.urls import path
from . import views

app_name = 'books'
urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('search/', views.search_view, name='search'),
    path('detail/<int:pk>/', views.book_detail_view, name='detail'),
    path('new-arrivals/', views.new_arrivals_view, name='new_arrivals'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('favorites/', views.favorites_view, name='favorites'),
]