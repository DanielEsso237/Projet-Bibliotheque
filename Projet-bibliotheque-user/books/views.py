from django.shortcuts import render
from django.db.models import Q
from .models import Book

def search_view(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    available = request.GET.get('available', False)

    books = Book.objects.all()
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
    if category:
        books = books.filter(category=category)
    if available:
        books = books.filter(is_available=True)

    categories = Book.objects.values_list('category', flat=True).distinct()

    context = {
        'books': books,
        'categories': categories,
        'query': query,
    }
    return render(request, 'books/search.html', context)

def loans_view(request):
    return render(request, 'books/loans.html')

def book_detail_view(request, pk):
    return render(request, 'books/book_detail.html')