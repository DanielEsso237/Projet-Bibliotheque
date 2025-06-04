from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.librarian_dashboard, name='librarian_dashboard'),
    path('choose-type/', views.choose_document_type, name='choose_document_type'),
    path('select-category/', views.select_document_category, name='select_document_category'),
    path('add-document/<str:document_type>/<str:academic_level>/', views.add_document, name='add_document'),
    path('add/', views.add_book, name='add_book'),
    path('delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('delete_doc/<int:doc_id>/', views.delete_doc, name='delete_doc'),
    path('edit_doc/<int:doc_id>/', views.edit_doc, name='edit_doc'),
    path('api/book/<int:book_id>/', views.book_api, name='book_api'),
    path('api/search/', views.search_books_api, name='search_books_api'),
    path('api/stats/', views.stats_api, name='stats_api'),
    path('api/doc/<int:doc_id>/', views.doc_api, name='doc_api'),
    path('api/doc_search/', views.search_docs_api, name='doc_search_api'),
    path('api/doc_stats/', views.doc_stats_api, name='doc_stats_api'),
]