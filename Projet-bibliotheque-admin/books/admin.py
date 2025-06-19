from django.contrib import admin
from .models import Book, Document

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category']
    list_filter = ['category']
    search_fields = ['title', 'author', 'isbn']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'document_type', 'academic_level', 'is_available']
    list_filter = ['document_type', 'academic_level', 'is_available']
    search_fields = ['title', 'author']
    readonly_fields = ['created_at', 'updated_at']