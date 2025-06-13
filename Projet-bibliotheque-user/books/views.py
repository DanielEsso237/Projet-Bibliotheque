from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from .models import Book, UserFavorite, Document
from loans.models import Loan, History
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
def dashboard_view(request):
    loans_count = Loan.objects.filter(user=request.user, is_returned=False).count()
    notifications_count = 0
    favorites_count = UserFavorite.objects.filter(user=request.user).count()
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

@login_required
def recommendations_view(request):
    genre_counts = (History.objects
                    .filter(user=request.user)
                    .values('genre')
                    .annotate(genre_count=Count('genre'))
                    .order_by('-genre_count'))
    top_genres = [item['genre'] for item in genre_counts[:3] if item['genre']]
    recommended_books = []
    if top_genres:
        recommended_books = (Book.objects
                            .filter(category__in=top_genres, is_available=True)
                            .order_by('-created_at')[:10])
    context = {
        'recommended_books': recommended_books,
        'message': 'Aucun livre recommandé pour le moment. Essayez d\'emprunter quelques livres pour des suggestions personnalisées.' if not recommended_books else ''
    }
    return render(request, 'books/recommendations.html', context)

@login_required
def favorites_view(request):
    favorite_books = Book.objects.filter(favorited_by__user=request.user)
    context = {
        'favorite_books': favorite_books,
        'message': 'Aucun livre en favoris.' if not favorite_books else ''
    }
    return render(request, 'books/favorites.html', context)

@require_POST
@login_required
def toggle_favorite(request):
    book_id = request.POST.get('book_id')
    book = get_object_or_404(Book, id=book_id)
    favorite, created = UserFavorite.objects.get_or_create(user=request.user, book=book)
    if not created:
        favorite.delete()
        return JsonResponse({'added': False})
    return JsonResponse({'added': True})

@login_required
def epreuves_view(request):
    levels = [level[0] for level in Document.ACADEMIC_LEVELS]
    selected_level = request.GET.get('level', '')
    epreuves = Document.objects.filter(document_type='exam')
    if selected_level:
        epreuves = epreuves.filter(academic_level=selected_level)
    context = {
        'epreuves': epreuves,
        'levels': levels,
    }
    return render(request, 'books/epreuves.html', context)

@login_required
def documents_view(request):
    document_types = Document.DOCUMENT_TYPES
    selected_type = request.GET.get('type', '')
    documents = Document.objects.all()
    if selected_type:
        documents = documents.filter(document_type=selected_type)
    context = {
        'documents': documents,
        'document_types': document_types,
    }
    return render(request, 'books/documents.html', context)

@login_required
def document_detail_view(request, pk):
    document = get_object_or_404(Document, pk=pk)
    context = {'document': document}
    return render(request, 'books/document_detail.html', context)