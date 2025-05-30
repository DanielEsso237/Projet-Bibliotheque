from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Book
from loans.models import Loan
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    loans_count = Loan.objects.filter(user=request.user, is_returned=False).count()
    notifications_count = 0
    favorites_count = 0

    context = {
        'loans_count': loans_count,
        'notifications_count': notifications_count,
        'favorites_count': favorites_count,
    }
    return render(request, 'books/dashboard.html', context)

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

def book_detail_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    context = {'book': book}
    return render(request, 'books/book_detail.html', context)

@login_required
def new_arrivals_view(request):
    recent_books = Book.objects.order_by('-created_at')[:10]
    context = {
        'recent_books': recent_books,
    }
    return render(request, 'books/new_arrivals.html', context)

def recommendations_view(request):
    return render(request, 'books/recommendations.html', {'message': 'Page en cours de développement'})

def favorites_view(request):
    return render(request, 'books/favorites.html', {'message': 'Page en cours de développement'})