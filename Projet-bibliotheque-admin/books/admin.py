from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_physical', 'is_available', 'quantity', 'category']
    list_filter = ['is_physical', 'is_available', 'category']
    search_fields = ['title', 'author', 'isbn']
    readonly_fields = ['created_at', 'updated_at']
