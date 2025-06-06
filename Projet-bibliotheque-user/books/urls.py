from django.urls import path
from . import views

app_name = 'books'
urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('search/', views.search_view, name='search'),
    path('details/<int:pk>/', views.book_detail_view, name='book_detail'),
    path('new-arrivals/', views.new_arrivals_view, name='new_arrivals'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('epreuves/', views.epreuves_view, name='epreuves'),
    path('documents/', views.documents_view, name='documents'),
]